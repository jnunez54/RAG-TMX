# RAG-TMX 
Implementación de un 🧠RAG para responder preguntas sobre Trámites Mexicanos!

### 📦 **Contenido** - [Instalación](#-instalación) - [Uso](#-uso) - [Descripción](#-descripción) - [To Do](#-to-do)
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
3. 
4. Con `test.ipynb` se puede realizar una ejecución de prompts predefinidos. Estos prompts prueban la conversacionalidad, fidelidad y filtro de las respuestas del asistente.

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