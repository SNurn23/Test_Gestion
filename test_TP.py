import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 

@pytest.fixture
def browser():
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    yield driver #permite devolver un valor y pausar su ejecución, pudiendo reanudarla más adelante desde donde se quedó.
    driver.quit()

def login(browser, username, password):
    browser.get("https://campusvirtual.ugd.edu.ar/moodle/login/index.php")
    browser.find_element(By.ID, "username").send_keys(username)
    browser.find_element(By.ID, "password").send_keys(password, Keys.RETURN)

#TEST CASE N°1: Inicio de sesión exitoso con credenciales válidas
def test_login_valid_credentials(browser):

    login(browser,"...", "...")
    
    # Verificar que el inicio de sesión fue exitoso redirigiendo a la página principal del campus
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

    login(browser,"...", "...")
    courseTitle = "GESTION DE LA CALIDAD Y AUDITORIA"

    #Se esperará un maximo de 10 segundos hasta que la sección "Mis cursos" se cargue en la página
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "frontpage-course-list")))    
    
    #Obtener el enlace del curso "GESTION DE LA CALIDAD Y AUDITORIA" en la lista de Mis cursos
    try:
       browser.find_element(By.LINK_TEXT, "GESTION DE LA CALIDAD Y AUDITORIA").click() #Va a buscar el elemento <a> que contenga el texto y una vez ubicado, hacer click en él
    except NoSuchElementException as err:
        pytest.fail(f"No se pudo acceder al curso: {str(err)}")

    WebDriverWait(browser, 10).until(EC.title_contains("GESTION DE LA CALIDAD Y AUDITORIA"))
    assert courseTitle in browser.title, "El título no coincide con el de la página"

#TEST CASE N°4: Visualización del siguiente texto en algún lugar del aula virtual, al iniciar sesión: 'no deberá registrar deuda luego del día 10 de cada mes.'
def test_verify_payment_due_text(browser):

    login(browser, "...", "...")

    #Se esperará un maximo de 10 segundos hasta que la sección "BLOQUEO DEL USUARIO" se cargue en la página
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "inst41282")))

    try:
        payment_due_text = browser.find_element(By.ID, "inst41282") #Obtendra el elemento donde se encuentra el anuncio de deuda
    except NoSuchElementException as err:
        pytest.fail(f"No se pudo acceder al anuncio de deuda: {str(err)}")

    #Va a verificar que dentro de ese bloque se encuentre el texto esperado
    assert "no deberá registrar deuda luego del día 10 de cada mes." in payment_due_text.text, "El texto no se encontró en el aula virtual" 

#Esto permite ejecutar el script para iniciar las pruebas.
if __name__ == "__main__": 
    pytest.main(["-v", "test_TP.py"])

