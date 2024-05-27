import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 

import time
import os

#VARIABLES DE CONFIRACION PARA EJECUCION DE PRUEBAS:
USER = "..."
PASSWORD = "..."
#Ruta donde se descargara pdf requerido por test 7 : 
RUTA_DESCARGA = r"C:\Users\axelx\Descargas"

@pytest.fixture  #funcion que se ejecutara antes(preparar el entorno necesario para ejecutar las pruebas) o despues(limpieza de resultados)
def browser():

    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": RUTA_DESCARGA, 
        "plugins.always_open_pdf_externally": True,
        "download.prompt_for_download": False,
        "directory_upgrade": True,
    }
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)

    driver.set_window_size(1200, 800)
    driver.implicitly_wait(10)
    yield driver #permite devolver un valor y pausar su ejecución, pudiendo reanudarla más adelante desde donde se quedó.
                 #Utiliza yield para devolver esta instancia a las pruebas que lo necesitan.
    driver.quit()

def login(browser, username, password):
    browser.get("https://campusvirtual.ugd.edu.ar/moodle/login/index.php")
    browser.find_element(By.ID, "username").send_keys(username)
    browser.find_element(By.ID, "password").send_keys(password, Keys.RETURN)

#TEST CASE N°1: Inicio de sesión exitoso con credenciales válidas
def test_login_valid_credentials(browser):

    login(browser,USER, PASSWORD)
    
    # Verificar que el inicio de sesión fue exitoso redirigiendo a la página principal del campuscls
    assert "https://campusvirtual.ugd.edu.ar/moodle/" == browser.current_url

#TEST CASE N°2: Error en inicio de sesión con credenciales inválidas
def test_login_invalid_credentials(browser):
    
    login(browser,"...", "...")

    try:
        error_message = browser.find_element(By.CLASS_NAME, "loginerrors")
        assert error_message.is_displayed(), "El mensaje de error no se mostró en la página de inicio de sesión"
    except NoSuchElementException as err:
        pytest.fail(f"El elemento del mensaje de error no se encontró en la página: {str(err)}")

#TEST CASE N°3: Titulo correcto al ingresar al aula de la materia
def test_correct_title_course(browser):

    login(browser,USER, PASSWORD)

    #Se esperará un maximo de 10 segundos hasta que la sección "Mis cursos" se cargue en la página
    WebDriverWait(browser, 60).until(EC.visibility_of_element_located((By.ID, "frontpage-course-list")))    
    
    #Obtener el enlace del curso "GESTION DE LA CALIDAD Y AUDITORIA" en la lista de Mis cursos
    try:
       browser.find_element(By.LINK_TEXT, "GESTION DE LA CALIDAD Y AUDITORIA").click() #Va a buscar el elemento <a> que contenga el texto y una vez ubicado, hacer click en él
    except NoSuchElementException as err:
        pytest.fail(f"No se pudo acceder al curso: {str(err)}")

    WebDriverWait(browser, 10).until(EC.title_contains("GESTION DE LA CALIDAD Y AUDITORIA"))
    assert "GESTION DE LA CALIDAD Y AUDITORIA" in browser.title, "El título no coincide con el de la página"

#TEST CASE N°4: Visualización del siguiente texto en algún lugar del aula virtual, al iniciar sesión: 'no deberá registrar deuda luego del día 10 de cada mes.'
def test_verify_payment_due_text(browser):

    login(browser,USER, PASSWORD)

    #Se esperará un maximo de 10 segundos hasta que la sección "BLOQUEO DEL USUARIO" se cargue en la página
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "inst41282")))

    try:
        payment_due_text = browser.find_element(By.ID, "inst41282") #Obtendra el elemento donde se encuentra el anuncio de deuda
    except NoSuchElementException as err:
        pytest.fail(f"No se pudo acceder al anuncio de deuda: {str(err)}")

    #Va a verificar que dentro de ese bloque se encuentre el texto esperado
    assert "no deberá registrar deuda luego del día 10 de cada mes." in payment_due_text.text, "El texto no se encontró en el aula virtual" 

#------------------------------------------------------------
# TEST CASE N°5: Búsqueda de materia exitosa desde "Todos los cursos"
def test_search_course_from_all_courses(browser):
    login(browser, USER, PASSWORD)
    
    # Navegar a la página "Todos los cursos"
    try:
        all_courses_link = browser.find_element(By.LINK_TEXT, "Todos los cursos")
        all_courses_link.click()
    except NoSuchElementException as err:
        pytest.fail(f"No se pudo encontrar el enlace 'Todos los cursos': {str(err)}")

    WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.ID, "coursesearchbox")))

    # Realizar la búsqueda del curso
    search_box = browser.find_element(By.ID, "coursesearchbox")
    search_box.send_keys("GESTION DE LA CALIDAD Y AUDITORIA", Keys.RETURN)

    WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, "coursebox")))

    try:
        course_link = browser.find_element(By.LINK_TEXT, "GESTION DE LA CALIDAD Y AUDITORIA")
        assert course_link.is_displayed(), "El curso no se encontró en los resultados de búsqueda"
        # Mantener el navegador abierto por 10 segundos para revisión manual
        time.sleep(3)
        course_link.click()  # Ingresar al curso
    except NoSuchElementException as err:
        pytest.fail(f"El curso 'GESTION DE LA CALIDAD Y AUDITORIA' no se encontró en los resultados de búsqueda: {str(err)}")
    
    # Verificar que se ha ingresado al curso comprobando el título de la página
    WebDriverWait(browser, 5).until(EC.title_contains("GESTION DE LA CALIDAD Y AUDITORIA"))
    assert "GESTION DE LA CALIDAD Y AUDITORIA" in browser.title, "No se ingresó al curso correctamente"

    # Mantener el navegador abierto por 10 segundos para revisión manual
    time.sleep(3)

# TEST CASE N°6: Visualización correcta del icono de tarea para "Gestor de Incidencias y Defectos"
def test_task_icon_displayed(browser):
    login(browser, USER, PASSWORD)
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "frontpage-course-list")))
    
    # Ingresar al curso "GESTION DE LA CALIDAD Y AUDITORIA"
    try:
        browser.find_element(By.LINK_TEXT, "GESTION DE LA CALIDAD Y AUDITORIA").click()
    except NoSuchElementException as err:
        pytest.fail(f"No se pudo acceder al curso: {str(err)}")
    
    # Esperar a que se cargue la página del curso
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "course-content")))

    # Buscar la tarea "Gestor de Incidencias y Defectos"
    try:
        task_element = browser.find_element(By.XPATH, "//span[text()='Gestor de Incidencias y Defectos']")
    except NoSuchElementException as err:
        pytest.fail(f"No se pudo encontrar la tarea 'Gestor de Incidencias y Defectos': {str(err)}")

    # Verificar que el icono de tarea está presente y visible junto al nombre de la tarea
    try:
        task_icon = task_element.find_element(By.XPATH, "./preceding-sibling::img[contains(@src, 'icon')]")
        assert task_icon.is_displayed(), "El icono de tarea no se muestra junto a 'Gestor de Incidencias y Defectos'"
    except NoSuchElementException as err:
        pytest.fail(f"No se pudo encontrar el icono de tarea junto a 'Gestor de Incidencias y Defectos': {str(err)}")

    # Mantener el navegador abierto por 10 segundos para revisión manual
    time.sleep(5)

#TEST CASE N°7: Descargas exitosa de pdf "Introducción a la Calidad y Pruebas de Software"
def test_download_pdf(browser):
    # Iniciar sesión
    login(browser, USER, PASSWORD)
    
    # Esperar a que aparezca la lista de cursos en la página principal
    WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.ID, "frontpage-course-list")))
    
    # Ingresar al curso "GESTION DE LA CALIDAD Y AUDITORIA"
    try:
        browser.find_element(By.LINK_TEXT, "GESTION DE LA CALIDAD Y AUDITORIA").click()
    except NoSuchElementException as err:
        pytest.fail(f"No se pudo acceder al curso: {str(err)}")
    
    # Esperar a que se cargue la página del curso
    WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, "course-content")))
    
    # Navegar al enlace del PDF
    pdf_link = "https://campusvirtual.ugd.edu.ar/moodle/mod/resource/view.php?id=99541"
    browser.get(pdf_link)
    
    # Esperar un momento para que el navegador cargue la página
    time.sleep(30)
    
    # Verificar que estamos en la página del PDF
    assert "Introducción a la Calidad y Pruebas de Software" in browser.title
    
    # Descargar el archivo PDF utilizando Selenium para interactuar con el botón de descarga
    try:
        # Si hay un iframe, cambiar al iframe del visualizador de PDF si es necesario
        iframes = browser.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            browser.switch_to.frame(iframes[0])
        
        # Buscar el enlace de descarga directamente en el documento
        download_button = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'pluginfile.php')]"))
        )
        download_url = download_button.get_attribute("href")
        browser.get(download_url)
    except (NoSuchElementException, TimeoutException) as err:
        pytest.fail(f"No se pudo encontrar el botón de descarga: {str(err)}")
    finally:
        # Volver al contenido principal si se cambió al iframe
        if iframes:
            browser.switch_to.default_content()
    
    # Esperar un momento para que se descargue el archivo
    time.sleep(5)
    
    # Verificar que el archivo se descargó correctamente
    download_dir = RUTA_DESCARGA
    file_name = "Clase 1.pdf"
    file_path = os.path.join(download_dir, file_name)
    assert os.path.exists(file_path), f"El archivo {file_name} no se descargó correctamente"
   
#------------------------------------------------------------
# TEST CASE N°8 : Se debe verificar que al iniciar sesión se visualice correctamente la respuesta a la pregunta frecuente “Todos tenemos USUARIO?”
def test_response_frequently_question(browser):
    login(browser,USER, PASSWORD)
    try:
        container = WebDriverWait(browser, 30).until(EC.visibility_of_element_located((By.ID, "circulos")))
        container.find_element(By.LINK_TEXT, "PREGUNTAS FRECUENTES").click()

        WebDriverWait(browser, 10)

        button = browser.find_element(By.XPATH,"//button[@class='accordion' and contains(text(), '¿Todos tenemos USUARIO?')]")
        button.click()
        respuesta = browser.find_element(By.XPATH,"//p[contains(text(), 'No, solo aquellos alumnos que Secretaria Acádemica valide que estén en regla con la Universidad.')]")
        
    except Exception as err:
        pytest.fail(f"No se a encotrado el boton con la pregunta:¿Todos tenemos USUARIO? o el elemento con la respuesta esperada no se a ecnotrado u desplegado al hacer click sobre el boton: {str(err)}")

    assert respuesta.is_displayed()

# TEST CASE N°9 : Verificación de materia en listado de “Perfiles de curso” desde el perfil del usuario. Se debe verificar que la materia se encuentra en la lista.
def test_materia_in_list_of_profile(browser):
    login(browser,USER, PASSWORD)
    try:
        WebDriverWait(browser, 10)
        container = browser.find_element(By.ID,"new-login")
        prefile = container.find_element(By.TAG_NAME,"a")
        prefile.click()

        WebDriverWait(browser, 10)

        list = browser.find_element(By.CLASS_NAME,"list")
        materia = list.find_element(By.XPATH,"//a[contains(text(), 'GESTION DE LA CALIDAD Y AUDITORIA')]")
  
    except Exception as err:
        pytest.fail(f"La materia no se a encotrado en la lista del perfil: {str(err)}")

    assert materia.is_displayed()

# TEST CASE N°10 : Verificación de cierre de sesión exitoso
def test_close_session(browser):
    login(browser,USER, PASSWORD)

    try:
        WebDriverWait(browser, 10)
        container = browser.find_element(By.ID,"new-login")
        prefile = container.find_elements(By.TAG_NAME,"a")[-1]
        prefile.click()

        WebDriverWait(browser, 10)

        form = browser.find_element(By.TAG_NAME,"form")
        form.find_element(By.TAG_NAME,"input").click()

        WebDriverWait(browser, 10)

        titleLogin = browser.title
        
    except Exception as err:
        pytest.fail(f"El cierre de sesion no fue exitoso: {str(err)}")

    assert titleLogin == "CAMPUS VIRTUAL UGD: Entrar al sitio"



#Esto permite ejecutar el script para iniciar las pruebas.
if __name__ == "__main__": 
    pytest.main(["-v", "tests.py"])

