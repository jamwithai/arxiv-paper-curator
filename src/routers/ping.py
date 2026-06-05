from fastapi import APIRouter
from sqlalchemy import text

from ..dependencies import DatabaseDep, OpenSearchDep, SettingsDep
from ..schemas.api.health import HealthResponse, ServiceStatus
from ..services.llm_factory import make_llm_client

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(settings: SettingsDep, database: DatabaseDep, opensearch_client: OpenSearchDep) -> HealthResponse:
    """Comprehensive health check endpoint for monitoring and load balancer probes.

    :returns: Service health status with version and connectivity checks
    :rtype: HealthResponse
    """
    services = {}
    overall_status = "ok"

    def _check_service(name: str, check_func, *args, **kwargs):
        """Helper to standardize service health checks."""
        try:
            if kwargs.get("is_async"):
                # Handle async functions separately in the calling code
                return check_func(*args)
            result = check_func(*args)
            services[name] = result
            if result.status != "healthy":
                nonlocal overall_status
                overall_status = "degraded"
        except Exception as e:
            services[name] = ServiceStatus(status="unhealthy", message=str(e))
            overall_status = "degraded"

    # Database check
    def _check_database():
        with database.get_session() as session:
            session.execute(text("SELECT 1"))
        return ServiceStatus(status="healthy", message="Connected successfully")

    # OpenSearch check
    def _check_opensearch():
        if not opensearch_client.health_check():
            return ServiceStatus(status="unhealthy", message="Not responding")
        stats = opensearch_client.get_index_stats()
        return ServiceStatus(
            status="healthy",
            message=f"Index '{stats.get('index_name', 'unknown')}' with {stats.get('document_count', 0)} documents",
        )

    # Run synchronous checks
    _check_service("database", _check_database)
    _check_service("opensearch", _check_opensearch)

    # Handle LLM provider async check separately
    try:
        llm_client = make_llm_client()
        llm_health = await llm_client.health_check()
        provider_name = settings.llm_provider
        services[provider_name] = ServiceStatus(status=llm_health["status"], message=llm_health["message"])
        if llm_health["status"] != "healthy":
            overall_status = "degraded"
    except Exception as e:
        services[settings.llm_provider] = ServiceStatus(status="unhealthy", message=str(e))
        overall_status = "degraded"

    return HealthResponse(
        status=overall_status,
        version=settings.app_version,
        environment=settings.environment,
        service_name=settings.service_name,
        services=services,
    )
