# RAG-TMX 
Implementación de un 🧠RAG para responder preguntas sobre Trámites Mexicanos!

### 📦 **Contenido** - [Instalación](#-instalación) - [Uso](#-uso) - [Descripción](#-descripción) - [To Do](#-to-do) - [Pruebas](#-pruebas)
## 🚀 Instalación
1. **Clonar el repositorio**
	```bash 
	git clone https://github.com/jnunez54/RAG-TMX.git
2. **Crear un venv e instalar los requerimientos**
	```bash 
	python -m venv venv 
	venv\Scripts\activate # Para Windows 
	pip install -r requirements.txt
3. **Instalar los binarios de playwright**
	```bash 
	python -m playwright install
## ⚙️ Uso
1. Configura la clave de la API de OpenAI en el archivo `config.py`
	 ```python 
	 OPENAI_API_KEY = "your_api_key"
2. La primera vez que se ejecuta `main.py` es necesario crear la base de datos. Puede tomar algo de tiempo ya que realiza las tareas de web scrapping, agrupamiento, vectorización y almacenamiento. 
3. Con `test.ipynb` se puede realizar una ejecución de prompts predefinidos. Estos prompts prueban la conversacionalidad, fidelidad y filtro de las respuestas del asistente.

## 📖 Descripción 

__Integraciones__: 
- 🦙[LlamaIndex](https://www.llamaindex.ai/) 
- 📚[Chroma](https://www.trychroma.com/)

## 📝 To Do
- [ ] Ajustar los parámetros de agrupamiento. 📚 
- [ ] Crear una interfáz de usuario. 💻 
- [ ] Integrar técnicas de post-procesamiento. 📝 
- [ ] Optimizar la generación de respuestas para aumentar la precisión. ⚡ 
- [ ] Implementar métricas de evaluación de fidelidad, coherencia, recuperación, etc... 🔄

## ✅ Pruebas
**Ejemplo de una conversación sobre los trámites disponibles**
```markdown
    User: Cuanto cuesta tramitar el CURP?
    Assistant: El trámite para obtener la Clave Única de Registro de Población (CURP) es gratuito. No se requiere ningún documento, pero es importante tener a la mano los datos de tu documento probatorio de identidad. 

    Para más información, puedes consultar la página oficial [aquí](https://www.gob.mx/tramites/ficha/consulta-e-impresion-de-la-curp/SEGOB175).

    User: Y el acta de nacimiento?
    Assistant: El costo para tramitar una copia certificada del acta de nacimiento varía según el estado en México. Aquí tienes algunos ejemplos de los costos:

    - Aguascalientes: $100.00 MXN
    - Ciudad de México: $94.00 MXN
    - Jalisco: $95.00 MXN
    - Veracruz: $199.00 MXN
    - Quintana Roo: $54.00 MXN

    Además, si necesitas solicitar una copia certificada en una oficina consular de México en el extranjero, el costo es de $19.00 USD.

    Para más información sobre los costos específicos en tu estado y el proceso de trámite, puedes consultar las siguientes páginas:

    - [Copia certificada del acta de nacimiento en oficina consular](https://www.gob.mx/tramites/ficha/copia-certificada-del-acta-de-nacimiento-autorizada-en-una-oficina-consular-de-mexico-en-el-exterior/SRE95)
    - [Expedición de la copia certificada del acta de nacimiento en línea](https://www.gob.mx/tramites/ficha/expedicion-de-la-copia-certificada-del-acta-de-nacimiento-en-linea/RENAPO187)

    User: Cuanto cuesta en Puebla
    Assistant: El costo para tramitar una copia certificada del acta de nacimiento en Puebla es de $160.00 MXN.

    Para más información sobre el trámite, puedes consultar la página oficial [aquí](https://www.gob.mx/tramites/ficha/expedicion-de-la-copia-certificada-del-acta-de-nacimiento-en-linea/RENAPO187).

    User: Que tramites son útiles si mi vehiculo fue robado
    Assistant: Lo siento, pero no tengo información disponible para responder tu pregunta en este momento. Si tienes otra consulta o necesitas ayuda con algo más, ¡estaré encantado de ayudarte!

    User: Debo pagar por reponer mi placa?
    Assistant: Sí, debes pagar por reponer la placa de tu vehículo. El costo para la reposición de placas metálicas es de $1,190.00 MXN. Además, si necesitas reponer la tarjeta de circulación, el costo es de $277.00 MXN.

    Para más información sobre el trámite, puedes consultar la página oficial [aquí](https://www.gob.mx/tramites/ficha/reposicion-de-tarjeta-de-circulacion-y-o-placas-metalicas-de-identificacion/SCT1438).

    User: La cartilla militar se puede tramitar en linea?
    Assistant: No se menciona específicamente en el contexto si se puede tramitar la cartilla militar en línea. Sin embargo, se indica que hay trámites que se pueden realizar en línea a través del Instituto de Seguridad Social para las Fuerzas Armadas Mexicanas (ISSFAM). Para obtener información más detallada sobre el trámite de la cartilla militar, te recomiendo consultar directamente en el sitio oficial del ISSFAM o en la página de trámites del gobierno.

    Puedes visitar el siguiente enlace para más información: [ISSFAM](https://www.gob.mx/tramites/ficha/pago-de-diferencias/ISSFAM8837).

    User: Y el pasaporte?
    Assistant: No se puede tramitar el pasaporte completamente en línea. Sin embargo, puedes realizar la cita en línea para el trámite del pasaporte en las Delegaciones de la Secretaría de Relaciones Exteriores (SRE) o en las Oficinas Estatales y Municipales de Enlace con la SRE. El trámite debe completarse de manera presencial.

    Para más información sobre el trámite del pasaporte, puedes consultar las siguientes páginas:

    - [Pasaporte Ordinario para Personas Mayores de Edad](https://www.gob.mx/tramites/ficha/pasaporte-ordinario-para-personas-mayores-de-edad/SRE112)
    - [Pasaporte Ordinario para Menores de Edad](https://www.gob.mx/tramites/ficha/pasaporte-ordinario-para-menores-de-edad-con-la-presencia-de-ambos-padres-o-quienes-ejercen-patria-potestad/SRE117)

    Si necesitas más detalles, no dudes en preguntar.

    User: Cómo crear un RAG desde 0
    Assistant: Lo siento, pero no tengo información disponible para responder tu pregunta en este momento. Si tienes otra consulta o necesitas ayuda con algo más, estaré encantado de intentar ayudarte.
