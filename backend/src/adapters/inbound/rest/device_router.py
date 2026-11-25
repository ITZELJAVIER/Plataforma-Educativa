from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from src.adapters.inbound.rest.device_schemas import (
    DeviceConfigRequest,
    DeviceCreateRequest,
    DeviceResponse,
    DeviceStateEventResponse,
)
from src.adapters.inbound.rest.router import (
    Authenticated,
    _http_error,
    get_authenticated,
)
from src.application.errors import ApplicationError
from src.application.use_cases.device_management import (
    DeviceConfigInput,
    DeviceInput,
    DeviceManagementService,
)
from src.domain.entities.device import DeviceView
from src.domain.entities.device_state_event import DeviceStateEvent

router = APIRouter(tags=["device-management"])


def get_device_service(request: Request) -> DeviceManagementService:
    return request.app.state.devices


def _response(view: DeviceView) -> DeviceResponse:
    return DeviceResponse(
        id=view.id,
        nombre=view.nombre,
        tipo=view.tipo,
        perfil_hardware=view.perfil_hardware,
        ubicacion=view.ubicacion,
        habilitado=view.habilitado,
        adaptador=view.adaptador,
        estado=view.estado.value,
    )


def _event_response(event: DeviceStateEvent) -> DeviceStateEventResponse:
    return DeviceStateEventResponse(
        device_id=event.device_id,
        estado_anterior=event.estado_anterior.value,
        estado_nuevo=event.estado_nuevo.value,
        ocurrido_en=event.ocurrido_en,
    )


@router.get("/devices", response_model=list[DeviceResponse])
def list_devices(
    auth: Authenticated = Depends(get_authenticated),
    service: DeviceManagementService = Depends(get_device_service),
) -> list[DeviceResponse]:
    try:
        views = service.list_devices(auth.token)
    except ApplicationError as exc:
        raise _http_error(exc) from exc
    return [_response(view) for view in views]


@router.get("/devices/{device_id}", response_model=DeviceResponse)
def get_device(
    device_id: str,
    auth: Authenticated = Depends(get_authenticated),
    service: DeviceManagementService = Depends(get_device_service),
) -> DeviceResponse:
    try:
        view = service.get_device(auth.token, device_id)
    except ApplicationError as exc:
        raise _http_error(exc) from exc
    return _response(view)


@router.post("/devices", response_model=DeviceResponse, status_code=201)
def register_device(
    payload: DeviceCreateRequest,
    auth: Authenticated = Depends(get_authenticated),
    service: DeviceManagementService = Depends(get_device_service),
) -> DeviceResponse:
    try:
        view = service.register_device(auth.token, DeviceInput(**payload.model_dump()))
    except ApplicationError as exc:
        raise _http_error(exc) from exc
    return _response(view)


@router.patch("/devices/{device_id}", response_model=DeviceResponse)
def update_device(
    device_id: str,
    payload: DeviceConfigRequest,
    auth: Authenticated = Depends(get_authenticated),
    service: DeviceManagementService = Depends(get_device_service),
) -> DeviceResponse:
    try:
        view = service.update_configuration(
            auth.token, device_id, DeviceConfigInput(**payload.model_dump())
        )
    except ApplicationError as exc:
        raise _http_error(exc) from exc
    return _response(view)


@router.post("/devices/{device_id}/deactivate", response_model=DeviceResponse)
def deactivate_device(
    device_id: str,
    auth: Authenticated = Depends(get_authenticated),
    service: DeviceManagementService = Depends(get_device_service),
) -> DeviceResponse:
    try:
        view = service.deactivate_device(auth.token, device_id)
    except ApplicationError as exc:
        raise _http_error(exc) from exc
    return _response(view)


@router.get(
    "/devices/{device_id}/events", response_model=list[DeviceStateEventResponse]
)
def list_device_events(
    device_id: str,
    auth: Authenticated = Depends(get_authenticated),
    service: DeviceManagementService = Depends(get_device_service),
) -> list[DeviceStateEventResponse]:
    try:
        events = service.list_events(auth.token, device_id)
    except ApplicationError as exc:
        raise _http_error(exc) from exc
    return [_event_response(event) for event in events]
