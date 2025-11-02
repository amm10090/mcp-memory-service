# Copyright 2024 Heinrich Krupp
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
OAuth 2.1 Authorization Server implementation for MCP Memory Service.

Implements OAuth 2.1 authorization code flow and token endpoints.
"""

import time
import logging
import base64
import hashlib
import hmac
import re
from typing import Optional, Tuple
from urllib.parse import urlencode
from fastapi import APIRouter, HTTPException, status, Form, Query, Request
from fastapi.responses import RedirectResponse
from jose import jwt

from ...config import (
    OAUTH_ISSUER,
    OAUTH_ACCESS_TOKEN_EXPIRE_MINUTES,
    OAUTH_AUTHORIZATION_CODE_EXPIRE_MINUTES,
    get_jwt_algorithm,
    get_jwt_signing_key
)
from .models import TokenResponse
from .storage import oauth_storage

logger = logging.getLogger(__name__)

router = APIRouter()

PKCE_ALLOWED_PATTERN = re.compile(r"^[A-Za-z0-9-._~]{43,128}$")
PKCE_SUPPORTED_METHODS = {"S256", "plain"}


def parse_basic_auth(authorization_header: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse HTTP Basic authentication header.

    Returns:
        Tuple of (client_id, client_secret) or (None, None) if not valid
    """
    if not authorization_header:
        return None, None

    try:
        # Check if it's Basic authentication
        if not authorization_header.startswith('Basic '):
            return None, None

        # Extract and decode the credentials
        encoded_credentials = authorization_header[6:]  # Remove 'Basic ' prefix
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')

        # Split username:password
        if ':' not in decoded_credentials:
            return None, None

        client_id, client_secret = decoded_credentials.split(':', 1)
        return client_id, client_secret

    except Exception as e:
        logger.debug(f"Failed to parse Basic auth header: {e}")
        return None, None


def create_access_token(client_id: str, scope: Optional[str] = None) -> tuple[str, int]:
    """
    Create a JWT access token for the given client.

    Uses RS256 with RSA key pair if available, otherwise falls back to HS256.

    Returns:
        Tuple of (token, expires_in_seconds)
    """
    expires_in = OAUTH_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    expire_time = time.time() + expires_in

    payload = {
        "iss": OAUTH_ISSUER,
        "sub": client_id,
        "aud": "mcp-memory-service",
        "exp": expire_time,
        "iat": time.time(),
        "scope": scope or "read write"
    }

    algorithm = get_jwt_algorithm()
    signing_key = get_jwt_signing_key()

    logger.debug(f"Creating JWT token with algorithm: {algorithm}")
    token = jwt.encode(payload, signing_key, algorithm=algorithm)
    return token, expires_in


def _normalize_code_challenge_method(method: Optional[str]) -> str:
    if not method:
        return "plain"

    if method.upper() == "S256":
        return "S256"

    if method.lower() == "plain":
        return "plain"

    return method


def _validate_pkce_value(value_name: str, value: str) -> None:
    if not PKCE_ALLOWED_PATTERN.match(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_request",
                "error_description": f"Invalid {value_name} format; must be 43-128 characters using [A-Za-z0-9-._~]"
            }
        )


def _compute_code_challenge(verifier: str, method: str) -> str:
    if method == "plain":
        return verifier
    if method == "S256":
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "error": "invalid_request",
            "error_description": f"Unsupported code challenge method: {method}"
        }
    )


async def validate_redirect_uri(client_id: str, redirect_uri: Optional[str]) -> str:
    """Validate redirect URI against registered client."""
    client = await oauth_storage.get_client(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_client",
                "error_description": "Invalid client_id"
            }
        )

    # If no redirect_uri provided, use the first registered one
    if not redirect_uri:
        if not client.redirect_uris:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "invalid_request",
                    "error_description": "redirect_uri is required when client has no registered redirect URIs"
                }
            )
        return client.redirect_uris[0]

    # Validate that the redirect_uri is registered
    if redirect_uri not in client.redirect_uris:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_redirect_uri",
                "error_description": "redirect_uri not registered for this client"
            }
        )

    return redirect_uri


@router.get("/authorize")
async def authorize(
    response_type: str = Query(..., description="OAuth response type"),
    client_id: str = Query(..., description="OAuth client identifier"),
    redirect_uri: Optional[str] = Query(None, description="Redirection URI"),
    scope: Optional[str] = Query(None, description="Requested scope"),
    state: Optional[str] = Query(None, description="Opaque value for CSRF protection"),
    code_challenge: Optional[str] = Query(None, description="PKCE code challenge"),
    code_challenge_method: Optional[str] = Query(None, description="PKCE code challenge method")
):
    """
    OAuth 2.1 Authorization endpoint.

    Implements the authorization code flow. For MVP, this auto-approves
    all requests without user interaction.
    """
    logger.info(f"Authorization request: client_id={client_id}, response_type={response_type}")

    try:
        # Validate response_type
        if response_type != "code":
            error_params = {
                "error": "unsupported_response_type",
                "error_description": "Only 'code' response type is supported"
            }
            if state:
                error_params["state"] = state

            # If we have a redirect_uri, redirect with error
            if redirect_uri:
                error_url = f"{redirect_uri}?{urlencode(error_params)}"
                return RedirectResponse(url=error_url)
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_params)

        # Validate client and redirect_uri
        validated_redirect_uri = await validate_redirect_uri(client_id, redirect_uri)
        client = await oauth_storage.get_client(client_id)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "invalid_client",
                    "error_description": "Invalid client_id"
                }
            )

        pkce_method = None
        if code_challenge_method and not code_challenge:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "invalid_request",
                    "error_description": "code_challenge_method supplied without code_challenge"
                }
            )

        if code_challenge:
            pkce_method = _normalize_code_challenge_method(code_challenge_method)

            if pkce_method not in PKCE_SUPPORTED_METHODS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "invalid_request",
                        "error_description": f"Unsupported code_challenge_method: {pkce_method}"
                    }
                )

            client_methods = getattr(client, "code_challenge_methods", ["plain"])
            if pkce_method not in client_methods:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "invalid_request",
                        "error_description": (
                            "Client is not registered for code_challenge_method "
                            f"{pkce_method}"
                        )
                    }
                )

            try:
                _validate_pkce_value("code_challenge", code_challenge)
            except HTTPException as exc:
                # Add redirect context below by raising immediately
                raise exc

        else:
            pkce_method = None

        # Generate authorization code
        auth_code = oauth_storage.generate_authorization_code()

        # Store authorization code
        await oauth_storage.store_authorization_code(
            code=auth_code,
            client_id=client_id,
            redirect_uri=validated_redirect_uri,
            scope=scope,
            expires_in=OAUTH_AUTHORIZATION_CODE_EXPIRE_MINUTES * 60,
            code_challenge=code_challenge,
            code_challenge_method=pkce_method,
        )

        # Build redirect URL with authorization code
        redirect_params = {"code": auth_code}
        if state:
            redirect_params["state"] = state

        redirect_url = f"{validated_redirect_uri}?{urlencode(redirect_params)}"

        logger.info(f"Authorization granted for client_id={client_id}")
        return RedirectResponse(url=redirect_url)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Authorization error: {e}")

        error_params = {
            "error": "server_error",
            "error_description": "Internal server error"
        }
        if state:
            error_params["state"] = state

        if redirect_uri:
            error_url = f"{redirect_uri}?{urlencode(error_params)}"
            return RedirectResponse(url=error_url)
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_params)


@router.post("/token", response_model=TokenResponse)
async def token(
    request: Request,
    grant_type: str = Form(..., description="OAuth grant type"),
    code: Optional[str] = Form(None, description="Authorization code"),
    redirect_uri: Optional[str] = Form(None, description="Redirection URI"),
    client_id: Optional[str] = Form(None, description="OAuth client identifier"),
    client_secret: Optional[str] = Form(None, description="OAuth client secret"),
    refresh_token: Optional[str] = Form(None, description="Refresh token value"),
    code_verifier: Optional[str] = Form(None, description="PKCE code verifier"),
):
    """
    OAuth 2.1 Token endpoint.

    Exchanges authorization codes for access tokens.
    Supports both authorization_code and client_credentials grant types.
    Supports both client_secret_post (form data) and client_secret_basic (HTTP Basic auth).
    """
    # Extract client credentials from either HTTP Basic auth or form data
    auth_header = request.headers.get('authorization')
    basic_client_id, basic_client_secret = parse_basic_auth(auth_header)

    # Use Basic auth credentials if available, otherwise fall back to form data
    final_client_id = basic_client_id or client_id
    final_client_secret = basic_client_secret or client_secret

    auth_method = "client_secret_basic" if basic_client_id else "client_secret_post"
    logger.info(f"Token request: grant_type={grant_type}, client_id={final_client_id}, auth_method={auth_method}")

    try:
        if grant_type == "authorization_code":
            # Validate required parameters
            if not code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "invalid_request",
                        "error_description": "Missing required parameter: code"
                    }
                )

            if not final_client_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "invalid_request",
                        "error_description": "Missing required parameter: client_id"
                    }
                )

            # Authenticate client
            if not await oauth_storage.authenticate_client(final_client_id, final_client_secret or ""):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": "invalid_client",
                        "error_description": "Client authentication failed"
                    }
                )

            # Get and consume authorization code
            code_data = await oauth_storage.get_authorization_code(code)
            if not code_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "invalid_grant",
                        "error_description": "Invalid or expired authorization code"
                    }
                )

            # Validate client_id matches
            if code_data["client_id"] != final_client_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "invalid_grant",
                        "error_description": "Authorization code was issued to a different client"
                    }
                )

            # Validate redirect_uri if provided
            if redirect_uri and code_data["redirect_uri"] != redirect_uri:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "invalid_grant",
                        "error_description": "redirect_uri does not match the one used in authorization request"
                    }
                )

            # PKCE validation
            stored_code_challenge = code_data.get("code_challenge")
            stored_code_method = code_data.get("code_challenge_method") or "plain"

            if stored_code_challenge:
                if not code_verifier:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error": "invalid_request",
                            "error_description": "Missing required parameter: code_verifier"
                        }
                    )

                _validate_pkce_value("code_verifier", code_verifier)

                expected_challenge = _compute_code_challenge(code_verifier, stored_code_method)

                if not hmac.compare_digest(stored_code_challenge, expected_challenge):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error": "invalid_grant",
                            "error_description": "Invalid code_verifier"
                        }
                    )

            elif code_verifier:
                # Client sent a verifier but no challenge was stored
                _validate_pkce_value("code_verifier", code_verifier)

            # Create access token
            access_token, expires_in = create_access_token(final_client_id, code_data["scope"])

            # Store access token for validation
            await oauth_storage.store_access_token(
                token=access_token,
                client_id=final_client_id,
                scope=code_data["scope"],
                expires_in=expires_in
            )

            refresh_token_value: Optional[str] = None
            client = await oauth_storage.get_client(final_client_id)
            if client and "refresh_token" in client.grant_types:
                refresh_token_value = oauth_storage.generate_refresh_token()
                await oauth_storage.store_refresh_token(
                    token=refresh_token_value,
                    client_id=final_client_id,
                    scope=code_data["scope"],
                )

            logger.info(f"Access token issued for client_id={final_client_id}")
            return TokenResponse(
                access_token=access_token,
                token_type="Bearer",
                expires_in=expires_in,
                scope=code_data["scope"],
                refresh_token=refresh_token_value,
            )

        elif grant_type == "client_credentials":
            # Client credentials flow for server-to-server authentication
            if not final_client_id or not final_client_secret:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "invalid_request",
                        "error_description": "Missing required parameters: client_id and client_secret"
                    }
                )

            # Authenticate client
            if not await oauth_storage.authenticate_client(final_client_id, final_client_secret):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": "invalid_client",
                        "error_description": "Client authentication failed"
                    }
                )

            # Create access token
            access_token, expires_in = create_access_token(final_client_id, "read write")

            # Store access token
            await oauth_storage.store_access_token(
                token=access_token,
                client_id=final_client_id,
                scope="read write",
                expires_in=expires_in
            )

            logger.info(f"Client credentials token issued for client_id={final_client_id}")
            return TokenResponse(
                access_token=access_token,
                token_type="Bearer",
                expires_in=expires_in,
                scope="read write"
            )

        elif grant_type == "refresh_token":
            if not refresh_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "invalid_request",
                        "error_description": "Missing required parameter: refresh_token"
                    }
                )

            if not final_client_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "invalid_request",
                        "error_description": "Missing required parameter: client_id"
                    }
                )

            if not await oauth_storage.authenticate_client(final_client_id, final_client_secret or ""):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": "invalid_client",
                        "error_description": "Client authentication failed"
                    }
                )

            client = await oauth_storage.get_client(final_client_id)
            if client and "refresh_token" not in client.grant_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "unauthorized_client",
                        "error_description": "Client is not authorized for refresh_token grant"
                    }
                )

            refresh_data = await oauth_storage.get_refresh_token(refresh_token)
            if not refresh_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "invalid_grant",
                        "error_description": "Invalid or expired refresh token"
                    }
                )

            if refresh_data["client_id"] != final_client_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "invalid_grant",
                        "error_description": "Refresh token was issued to a different client"
                    }
                )

            access_token, expires_in = create_access_token(final_client_id, refresh_data["scope"])

            await oauth_storage.store_access_token(
                token=access_token,
                client_id=final_client_id,
                scope=refresh_data["scope"],
                expires_in=expires_in
            )

            await oauth_storage.revoke_refresh_token(refresh_token)
            new_refresh_token = oauth_storage.generate_refresh_token()
            await oauth_storage.store_refresh_token(
                token=new_refresh_token,
                client_id=final_client_id,
                scope=refresh_data["scope"],
            )

            logger.info(f"Refresh token exchanged for new access token for client_id={final_client_id}")
            return TokenResponse(
                access_token=access_token,
                token_type="Bearer",
                expires_in=expires_in,
                scope=refresh_data["scope"],
                refresh_token=new_refresh_token,
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "unsupported_grant_type",
                    "error_description": f"Grant type '{grant_type}' is not supported"
                }
            )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Token endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "server_error",
                "error_description": "Internal server error"
            }
        )
