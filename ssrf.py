import re
from urllib.parse import quote

import requests
from fastapi import APIRouter, HTTPException, Response


# Set up FastAPI router
msys2 = APIRouter(prefix="/msys2")

# List of valid inputs, used over multiple endpoints
valid_env = ("msys", "mingw")
valid_msys = ("i686", "x86_64")
valid_mingw = (
    "clang32",
    "clang64",
    "clangarm64",
    "i686",
    "mingw32",
    "mingw64",
    "sources",
    "ucrt64",
    "x86_64",
)


@msys2.get("/{environment}/{architecture}/{package}", response_class=Response)
def get_msys2_package_file(
    environment: str,
    architecture: str,
    package: str,
) -> Response:
    """
    Obtain and pass through a specific download for an MSYS2 package.
    """

    # Validate environment
    if environment not in valid_env:
        raise ValueError(f"{environment!r} is not a valid msys2 environment")

    # Validate architecture for each environment
    if environment == "msys" and architecture not in valid_msys:
        raise ValueError(f"{architecture!r} is not a valid msys architecture")
    elif environment == "mingw" and architecture not in valid_mingw:
        raise ValueError(f"{architecture!r} is not a valid mingw architecture")

    # Validate package name
    if bool(re.fullmatch(r"^[\w\s\.\-]+$", package)) is False:
        raise ValueError(f"{package!r} is not a valid package name")

    # Construct URL to main MSYS repo and get response
    package_url = f"https://repo.msys2.org/{quote(environment)}/{quote(architecture)}/{quote(package)}"
    package_file = requests.get(package_url)

    if package_file.status_code == 200:
        return Response(
            content=package_file.content,
            media_type=package_file.headers.get("Content-Type"),
            status_code=package_file.status_code,
        )
    else:
        raise HTTPException(status_code=package_file.status_code)
