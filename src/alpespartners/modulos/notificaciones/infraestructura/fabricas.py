from dataclasses import dataclass

from alpespartners.seedwork.dominio.fabricas import Fabrica
from alpespartners.seedwork.dominio.excepciones import ExcepcionFabrica
from .proveedores import EmailProvider, MockEmailProvider


@dataclass
class FabricaEmailProviders(Fabrica):
    """Factory para crear proveedores de email"""
    
    def crear_objeto(self, tipo_proveedor: str) -> EmailProvider:
        """
        Crea un proveedor de email según el tipo especificado
        
        Args:
            tipo_proveedor: Tipo de proveedor ('mock')
            
        Returns:
            EmailProvider: Instancia del proveedor de email
            
        Raises:
            ExcepcionFabrica: Si el tipo de proveedor no es válido
        """
        tipo_proveedor = tipo_proveedor.lower()
        
        if tipo_proveedor == 'mock':
            return self._crear_proveedor_mock()
        else:
            raise ExcepcionFabrica(f"Tipo de proveedor de email no válido: {tipo_proveedor}. Solo se soporta 'mock'")
    
    def _crear_proveedor_mock(self) -> MockEmailProvider:
        """Crea un proveedor mock para testing"""
        return MockEmailProvider()
    
    def crear_proveedor_por_configuracion(self) -> EmailProvider:
        """
        Crea un proveedor de email basado en las variables de entorno
        
        Returns:
            EmailProvider: Instancia del proveedor de email configurado (siempre mock)
        """
        return self._crear_proveedor_mock()
