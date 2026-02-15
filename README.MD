# 🖥️ Server Panel

Server Panel es un panel web ligero desarrollado en Python con FastAPI que permite administrar y monitorizar un servidor Debian desde el navegador.

El objetivo del proyecto es proporcionar una interfaz sencilla, segura y minimalista para gestionar recursos del sistema y controlar servicios críticos sin necesidad de acceder constantemente por terminal.

---

## 🎯 Objetivo

Centralizar en una única interfaz web:

* Monitorización del sistema
* Gestión de usuarios con roles
* Control de servicios systemd
* Autenticación segura

Pensado especialmente para entornos domésticos, homelabs o servidores personales.

---

## 🧠 Funcionamiento

El panel se ejecuta como un servicio del sistema (systemd) y expone una interfaz web accesible desde la red.

Internamente utiliza:

* **FastAPI** como framework backend
* **Jinja2** para renderizado de plantillas HTML
* **Argon2** para el hash seguro de contraseñas
* **SQLite** como base de datos ligera
* **systemctl** para controlar servicios del sistema
* **psutil** para obtener métricas del servidor

El sistema está diseñado para ejecutarse con un usuario dedicado y con permisos sudo limitados únicamente a los servicios permitidos.

---

## 👥 Sistema de usuarios

El panel incluye:

* Autenticación con sesiones
* Roles diferenciados:

  * `admin` → control total
  * `viewer` → solo visualización
* Activación/desactivación de cuentas
* Cambio de contraseña y rol
* Eliminación de usuarios

Las contraseñas nunca se almacenan en texto plano.

---

## 📊 Monitorización

Muestra en tiempo real:

* Uso de CPU
* Uso de RAM
* Uso de disco
* Tiempo de actividad (uptime)

La información se actualiza automáticamente desde el frontend mediante peticiones a la API.

---

## ⚙️ Control de servicios

Permite iniciar, detener y reiniciar servicios específicos del sistema:

* SSH
* Pi-hole
* WireGuard

El acceso está restringido mediante configuración de sudo para evitar privilegios excesivos.

---

## 🔐 Seguridad

* No se ejecuta como root
* Permisos sudo limitados a comandos concretos
* Protección contra inyección en subprocess
* Manejo de errores con páginas HTML personalizadas
* Separación clara entre lógica, rutas y frontend

---

## 🏗️ Arquitectura

El proyecto sigue una estructura modular:

* `core/` → seguridad, autenticación y base de datos
* `routers/` → endpoints organizados por funcionalidad
* `services/` → lógica del sistema (monitorización y systemctl)
* `web/` → plantillas y archivos estáticos

---

## 📌 Enfoque del proyecto

Server Panel está diseñado para ser:

* Ligero
* Seguro
* Fácil de desplegar
* Modular y escalable
* Adaptado a servidores Debian

Es una solución práctica para quienes desean una capa de administración web sobre su servidor sin depender de herramientas pesadas o externas.

---