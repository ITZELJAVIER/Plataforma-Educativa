from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from src.adapters.inbound.rest.peripheral_schemas import (
    PeripheralMetadataUpdateRequest,
    PeripheralTypeCreateRequest,
    PeripheralTypeResponse,
    ValueRequest,
    ValueValidationResponse,
)
from src.adapters.inbound.rest.router import (
    Authenticated,
    _http_error,
    get_authenticated,
)
from src.application.errors import ApplicationError
from src.application.use_cases.peripheral_catalog import (
    PeripheralCatalogService,
    PeripheralTypeInput,
)
from src.domain.entities.peripheral_type import PeripheralType

router = APIRouter(tags=["peripheral-catalog"])


def get_catalog_service(request: Request) -> PeripheralCatalogService:
    return request.app.state.peripheral_catalog


def _response(definition: PeripheralType) -> PeripheralTypeResponse:
    return PeripheralTypeResponse(**definition.to_dict())


@router.get("/peripherals/types", response_model=list[PeripheralTypeResponse])
def list_types(
    auth: Authenticated = Depends(get_authenticated),
    service: PeripheralCatalogService = Depends(get_catalog_service),
) -> list[PeripheralTypeResponse]:
    try:
        definitions = service.list_types(auth.token)
    except ApplicationError as exc:
        raise _http_error(exc) from exc
    return [_response(definition) for definition in definitions]


@router.get("/peripherals/types/{tipo}", response_model=PeripheralTypeResponse)
def get_type(
    tipo: str,
    auth: Authenticated = Depends(get_authenticated),
    service: PeripheralCatalogService = Depends(get_catalog_service),
) -> PeripheralTypeResponse:
    try:
        definition = service.get_type(auth.token, tipo)
    except ApplicationError as exc:
        raise _http_error(exc) from exc
    return _response(definition)


@router.post(
    "/peripherals/types",
    response_model=PeripheralTypeResponse,
    status_code=201,
)
def register_type(
    payload: PeripheralTypeCreateRequest,
    auth: Authenticated = Depends(get_authenticated),
    service: PeripheralCatalogService = Depends(get_catalog_service),
) -> PeripheralTypeResponse:
    try:
        definition = service.register_type(
            auth.token, PeripheralTypeInput(**payload.model_dump())
        )
    except ApplicationError as exc:
        raise _http_error(exc) from exc
    return _response(definition)


@router.patch("/peripherals/types/{tipo}", response_model=PeripheralTypeResponse)
def update_type(
    tipo: str,
    payload: PeripheralMetadataUpdateRequest,
    auth: Authenticated = Depends(get_authenticated),
    service: PeripheralCatalogService = Depends(get_catalog_service),
) -> PeripheralTypeResponse:
    try:
        definition = service.update_type(
            auth.token, tipo, PeripheralTypeInput(**payload.model_dump())
        )
    except ApplicationError as exc:
        raise _http_error(exc) from exc
    return _response(definition)


@router.post(
    "/peripherals/types/{tipo}/validate-value",
    response_model=ValueValidationResponse,
)
def validate_value(
    tipo: str,
    payload: ValueRequest,
    auth: Authenticated = Depends(get_authenticated),
    service: PeripheralCatalogService = Depends(get_catalog_service),
) -> ValueValidationResponse:
    try:
        definition = service.validate_value(auth.token, tipo, payload.valor)
    except ApplicationError as exc:
        raise _http_error(exc) from exc
    return ValueValidationResponse(valido=True, tipo=definition.tipo)
