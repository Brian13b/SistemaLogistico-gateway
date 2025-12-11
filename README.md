# 🚀 API Gateway - Sistema Logístico

Este microservicio actúa como el **punto único de entrada** para todo el ecosistema del Sistema Logístico. Su responsabilidad es orquestar las peticiones del frontend, enrutarlas al microservicio correcto y garantizar la seguridad global.

---

## 🌟 Funcionalidades Principales
- **Centralización:** Unifica múltiples APIs (Backend, Tracking, Facturación) bajo un solo dominio.
- **Seguridad (AuthN/AuthZ):** Valida tokens **JWT** antes de permitir el paso a servicios protegidos.
- **Enrutamiento Inteligente:** Redirige tráfico HTTP basándose en prefijos de URL.
- **Limpieza de API:** Desacopla al cliente de la estructura interna de la red.

---

## 📚 Flujo de Petición
1.  🌐 **Cliente:** Envía `GET /api/viajes` con Header `Authorization: Bearer <token>`.
2.  🛡️ **Gateway:** Intercepta, decodifica y valida la firma y expiración del JWT.
3.  ✅ **Validación:**
    - *Token Inválido:* Retorna `401 Unauthorized`.
    - *Token Válido:* Pasa la petición al servicio `backend-core:8001`.
4.  🔄 **Proxy:** Recibe la respuesta del microservicio y la entrega al cliente.

---

## 🛡️ Stack Tecnológico
- **Lenguaje:** Python 3.10+
- **Framework:** FastAPI
- **Seguridad:** PyJWT
- **Cliente HTTP:** Httpx (Async)

---

## 🌱 Futuras Actualizaciones
- [ ] **Rate Limiting:** Protección contra ataques DDoS y abuso de API.
- [ ] **Cacheo de Respuestas:** Implementar Redis para cachear respuestas frecuentes.
- [ ] **Documentación Unificada:** Fusionar Swagger/OpenAPI de todos los microservicios en una sola UI.
- [ ] **Logging Centralizado:** Envío de logs a una pila ELK o Grafana Loki.

---

## 👤 Autor
**Brian Battauz** - [GitHub](https://github.com/Brian13b)