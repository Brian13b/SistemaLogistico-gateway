# 🚀 API Gateway del sistema de gestión de flotas.

Este módulo forma parte del ecosistema **Sistema Logistico** y actúa como punto central de entrada para todas las solicitudes que provienen del frontend. Se encarga de enrutar las peticiones hacia los microservicios correspondientes, además de aplicar políticas de autenticación y autorización a nivel global.

---

🌟 **¿Qué hace este módulo?**  
- Centraliza el acceso a todos los microservicios del sistema.  
- Dirige las solicitudes del frontend a los servicios correspondientes mediante reglas de enrutamiento.  
- Gestiona la autenticación y autorización utilizando **JWT**, protegiendo todos los recursos del sistema.  
- Simplifica la arquitectura del frontend al exponer un único punto de entrada para toda la API.

---

🔧 **Características principales**  
- 🔐 Autenticación y autorización global con **JSON Web Tokens (JWT)**.  
- 🔀 Enrutamiento inteligente hacia los distintos microservicios.  
- 🛡️ Punto de control para la seguridad de todas las rutas.  
- ⚖️ Escalabilidad mediante balanceo de carga y desacoplamiento de servicios.

---

📚 **Ejemplo de flujo de trabajo**  
1. 🌐 El usuario envía una solicitud desde el frontend.  
2. 🔐 El gateway valida el token JWT.  
3. 📨 Si es válido, redirige la petición al microservicio correspondiente.  
4. 📊 Devuelve la respuesta al usuario desde el microservicio a través del gateway.

---

🛡️ **Tecnologías Usadas**  
- 🖥️ Lenguaje: Python  
- ⚡ Framework: FastAPI  
- 🔒 Autenticación: JWT  
- 🌐 Protocolo: HTTP/REST

---

🌱 **Futuras actualizaciones**  
- 📊 Integración con servicios de monitoreo (Prometheus, Grafana, etc.).  
- 🌍 Soporte para internacionalización y configuración dinámica de rutas.  
- 🚨 Registro centralizado de logs y trazabilidad de peticiones.

---