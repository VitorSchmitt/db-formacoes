from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse

router = APIRouter()

# fake (depois liga no banco)
USUARIOS = {
    "admin": {"senha": "147", "perfil": "admin"},
    "user": {"senha": "147", "perfil": "operador"}
}


@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = USUARIOS.get(username)

    if not user or user["senha"] != password:
        return JSONResponse(status_code=401, content={"erro": "Login inválido"})

    request.session["user"] = {
        "username": username,
        "perfil": user["perfil"]
    }

    return RedirectResponse("/web/dashboard", status_code=302)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=302)
