"""Errores comunes a los adaptadores de proveedor (LLM y embeddings)."""


class ProveedorNoSoportadoError(ValueError):
    """LLM_PROVIDER/EMBEDDING_PROVIDER no tiene un adaptador registrado.

    Se lanza al arrancar la app (fail-fast), no en medio de una request.
    """

    def __init__(self, tipo: str, proveedor: str, soportados: list[str]) -> None:
        self.tipo = tipo
        self.proveedor = proveedor
        self.soportados = soportados
        super().__init__(
            f"Proveedor de {tipo} no soportado: '{proveedor}'. "
            f"Proveedores soportados: {', '.join(soportados)}."
        )


class EmbeddingRateLimitError(RuntimeError):
    """Límite de tasa alcanzado en el proveedor de embeddings configurado."""
