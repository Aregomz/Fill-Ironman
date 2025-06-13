import random
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


# PINCHE EDIIWI NO ME PAGO ALB
# === CONFIGURACIÓN ===
NUM_RESPUESTAS = 5  # Cambia este número a la cantidad de respuestas que quieres
TIEMPO_MIN = 5    # Tiempo mínimo entre respuestas (en segundos)
TIEMPO_MAX = 10    # Tiempo máximo entre respuestas (en segundos)
FORM_URL = "https://forms.gle/LY9XAVNtenSwjjREA"
EDGE_DRIVER_PATH = r"C:\Users\arell\Downloads\edgedriver_win32\msedgedriver.exe"

# Lista de preguntas que deben ser respondidas
PREGUNTAS = [
    "¿Actualmente posee algún vehículo automotor",
    "Tipo principal de vehículo que utiliza",
    "Frecuencia promedio de uso del vehículo",
    "Calles con poca iluminación",
    "Zonas donde usted considera o sabe que han ocurrido asaltos",
    "Vías poco transitadas o aisladas",
    "Áreas donde ha presenciado o escuchado de robos",
    "Al caminar solo(a) de noche por su colonia",
    "Al usar transporte público",
    "Al transitar en automóvil",
    "En su propio hogar",
    "En centros comerciales o espacios públicos",
    "¿Ha sido víctima directa de algún delito",
    "¿Conoce a alguien cercano",
    "En su opinión, ¿la inseguridad en su ciudad",
    "¿Cuenta actualmente con algún tipo de seguro",
    "En general, ¿cuál de las siguientes opciones describe mejor su disposición",
    "¿Cuál de las siguientes razones describe mejor",
    "¿Considera que tener un seguro vehicular",
    "Costo del seguro",
    "Inseguridad relacionada con robo o vandalismo",
    "Inseguridad relacionada con accidentes viales",
    "Inseguridad general en su ciudad o colonia",
    "Opiniones o consejos de personas cercanas",
    "Experiencia previa con aseguradoras",
    "Nivel de uso del vehículo",
    "Contrato seguros por precaución",
    "¿Ha contratado personalmente un seguro vehicular",
    "¿Considera que entiende bien los beneficios",
    "En su opinión, ¿las aseguradoras en México",
    "¿Ha recibido información o asesoría",
    "¿Qué tan fácil o difícil le resulta encontrar"
]
# ======================

# Función para hacer clic en opción con texto (evitando "Otro")
def click_option(driver, label_text):
    try:
        xpath = f'//span[contains(text(), "{label_text}")]'
        option = driver.find_element(By.XPATH, xpath)
        option.click()
        time.sleep(0.5)
    except:
        pass

# Función para obtener opciones válidas (sin "Otro" o "Otra")
def obtener_opciones_validas(opciones_lista):
    """
    Filtra las opciones para remover cualquier opción que contenga 'Otro' o 'Otra'
    """
    opciones_filtradas = []
    for opcion in opciones_lista:
        # Convertir a minúsculas para comparación
        opcion_lower = opcion.lower()
        # Evitar opciones que contengan "otro" o "otra"
        if not any(palabra in opcion_lower for palabra in ['otro', 'otra', 'other']):
            opciones_filtradas.append(opcion)
    
    # Si todas las opciones fueron filtradas, devolver la lista original
    return opciones_filtradas if opciones_filtradas else opciones_lista

def responder_pregunta_radio_mejorada(driver, pregunta_texto, intentos=3):
    """
    Función mejorada para responder preguntas de radio con múltiples estrategias
    """
    print(f"   Intentando responder: '{pregunta_texto[:40]}...'")
    
    for intento in range(intentos):
        try:
            # Hacer scroll gradual para cargar contenido
            driver.execute_script("window.scrollBy(0, 200);")
            time.sleep(0.5)
            
            # Estrategia 1: Buscar por texto exacto en span
            contenedores_encontrados = []
            
            # Múltiples formas de buscar la pregunta
            selectors = [
                f"//span[contains(text(), '{pregunta_texto}')]",
                f"//div[contains(text(), '{pregunta_texto}')]",
                f"//*[contains(text(), '{pregunta_texto}')]"
            ]
            
            for selector in selectors:
                elementos = driver.find_elements(By.XPATH, selector)
                for elemento in elementos:
                    # Buscar el contenedor padre que tenga opciones de radio
                    contenedor = elemento
                    for _ in range(10):  # Buscar hasta 10 niveles arriba
                        opciones_radio = contenedor.find_elements(By.XPATH, './/div[@role="radio"]')
                        if opciones_radio:
                            contenedores_encontrados.append(contenedor)
                            break
                        try:
                            contenedor = contenedor.find_element(By.XPATH, '..')
                        except:
                            break
            
            # Si no encontramos contenedores, intentar búsqueda más amplia
            if not contenedores_encontrados:
                # Buscar todas las opciones de radio en la página
                todas_opciones = driver.find_elements(By.XPATH, '//div[@role="radio"]')
                if todas_opciones:
                    # Agrupar por contenedor padre
                    contenedores_temp = set()
                    for opcion in todas_opciones:
                        try:
                            # Buscar contenedor padre común
                            contenedor = opcion
                            for _ in range(5):
                                contenedor = contenedor.find_element(By.XPATH, '..')
                                opciones_en_contenedor = contenedor.find_elements(By.XPATH, './/div[@role="radio"]')
                                if len(opciones_en_contenedor) >= 2:  # Al menos 2 opciones
                                    contenedores_temp.add(contenedor)
                                    break
                        except:
                            continue
                    contenedores_encontrados = list(contenedores_temp)
            
            # Procesar contenedores encontrados
            for contenedor in contenedores_encontrados:
                try:
                    # Verificar si ya está respondida
                    opciones_marcadas = contenedor.find_elements(By.XPATH, './/div[@role="radio" and @aria-checked="true"]')
                    
                    if opciones_marcadas:
                        # Verificar si la opción marcada es válida (no "Otro")
                        texto_marcado = ""
                        try:
                            texto_marcado = opciones_marcadas[0].find_element(By.XPATH, './/span').text.lower()
                        except:
                            pass
                            
                        if not any(palabra in texto_marcado for palabra in ['otro', 'otra', 'other', 'especifica']):
                            print(f"   [OK] Ya respondida correctamente: '{pregunta_texto[:30]}...'")
                            return True
                    
                    # Obtener opciones disponibles
                    opciones_disponibles = contenedor.find_elements(By.XPATH, './/div[@role="radio"]')
                    opciones_validas = []
                    
                    for opcion in opciones_disponibles:
                        try:
                            texto_opcion = opcion.find_element(By.XPATH, './/span').text.lower()
                            # Filtrar opciones "Otro" o similares
                            if not any(palabra in texto_opcion for palabra in ['otro', 'otra', 'other', 'especifica', 'especificar']):
                                opciones_validas.append(opcion)
                        except:
                            # Si no se puede obtener el texto, incluir la opción
                            opciones_validas.append(opcion)
                    
                    # Seleccionar una opción válida aleatoriamente
                    if opciones_validas:
                        opcion_elegida = random.choice(opciones_validas)
                        
                        # Hacer scroll hasta la opción
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", opcion_elegida)
                        time.sleep(1)
                        
                        # Intentar diferentes métodos de clic
                        exito_clic = False
                        metodos_clic = [
                            lambda: opcion_elegida.click(),
                            lambda: driver.execute_script("arguments[0].click();", opcion_elegida),
                            lambda: ActionChains(driver).move_to_element(opcion_elegida).click().perform(),
                            lambda: driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));", opcion_elegida)
                        ]
                        
                        for i, metodo in enumerate(metodos_clic):
                            try:
                                metodo()
                                time.sleep(0.5)
                                
                                # Verificar si se marcó correctamente
                                if opcion_elegida.get_attribute('aria-checked') == 'true':
                                    print(f"   [OK] Respondida con método {i+1}: '{pregunta_texto[:30]}...'")
                                    exito_clic = True
                                    break
                            except Exception as e:
                                continue
                        
                        if exito_clic:
                            return True
                        else:
                            print(f"   [ADVERTENCIA] No se pudo marcar la opción para '{pregunta_texto[:30]}...'")
                    
                except Exception as e:
                    print(f"   [ERROR] Error procesando contenedor: {str(e)[:50]}")
                    continue
            
            if not contenedores_encontrados:
                print(f"   [ADVERTENCIA] No se encontró la pregunta '{pregunta_texto[:30]}...' (intento {intento + 1})")
            
        except Exception as e:
            print(f"   [ERROR] Error general en intento {intento + 1}: {str(e)[:50]}")
        
        # Esperar antes del siguiente intento
        time.sleep(1)
    
    print(f"   [ERROR] No se pudo responder '{pregunta_texto[:30]}...' después de {intentos} intentos")
    return False

def responder_todas_las_preguntas(driver):
    """
    Función para responder todas las preguntas de radio de forma secuencial
    """
    print("   Respondiendo todas las preguntas de radio...")
    
    # Primero, hacer scroll completo para cargar toda la página
    print("   Cargando contenido completo de la página...")
    altura_anterior = 0
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        altura_actual = driver.execute_script("return document.body.scrollHeight")
        if altura_actual == altura_anterior:
            break
        altura_anterior = altura_actual
    
    # Volver al inicio
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)
    
    # Responder cada pregunta
    preguntas_exitosas = 0
    for i, pregunta in enumerate(PREGUNTAS):
        print(f"   Pregunta {i+1}/{len(PREGUNTAS)}: Procesando...")
        if responder_pregunta_radio_mejorada(driver, pregunta):
            preguntas_exitosas += 1
        time.sleep(0.5)  # Pausa entre preguntas
    
    print(f"   [RESUMEN] Se respondieron {preguntas_exitosas} de {len(PREGUNTAS)} preguntas")
    return preguntas_exitosas == len(PREGUNTAS)

# Función mejorada para llenar el campo de Entidad Federativa
def llenar_entidad_federativa(driver):
    """
    Función específica para llenar el campo de Entidad Federativa con 'Chiapas'
    """
    metodos = [
        lambda: driver.find_elements(By.XPATH, '//div[contains(text(), "Entidad federativa")]//following::input[@type="text"]')[0],
        lambda: driver.find_elements(By.XPATH, '//span[contains(text(), "Entidad federativa")]//following::input[@type="text"]')[0],
        lambda: driver.find_element(By.XPATH, '//input[contains(@aria-label, "Entidad") or contains(@aria-label, "entidad")]'),
        lambda: driver.find_elements(By.XPATH, '//input[@type="text"]')[1],
        lambda: next((inp for inp in driver.find_elements(By.XPATH, '//input[@type="text"]') 
                     if not inp.get_attribute('value')), None)
    ]
    
    for i, metodo in enumerate(metodos, 1):
        try:
            print(f"   Intentando método {i} para Entidad Federativa...")
            campo = metodo()
            if campo:
                campo.clear()
                campo.send_keys("Chiapas")
                print("   [OK] Campo 'Entidad Federativa' llenado con 'Chiapas'")
                return True
        except Exception as e:
            print(f"   [ERROR] Método {i} falló: {str(e)[:50]}...")
            continue
    
    print("   [ADVERTENCIA] No se pudo llenar el campo de Entidad Federativa")
    return False

# Función que llena y envía el formulario una vez
def llenar_formulario():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--user-data-dir=C:\\temp\\EdgeProfile_" + str(random.randint(1000, 9999)))
    service = Service(EDGE_DRIVER_PATH)
    driver = webdriver.Edge(service=service, options=options)
    
    # Ejecutar script para ocultar que es automatizado
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        driver.get(FORM_URL)
        print("   Cargando formulario...")
        time.sleep(5)  # Esperar más tiempo para carga completa

        # Edad - Campo de texto numérico
        print("   Llenando edad...")
        edad = str(random.randint(18, 53))
        try:
            input_edad = driver.find_elements(By.XPATH, '//input[@type="text"]')[0]
            input_edad.clear()
            input_edad.send_keys(edad)
            print(f"   [OK] Edad: {edad}")
        except Exception as e:
            print(f"   [ERROR] Error al llenar edad: {e}")

        time.sleep(1)

        # Entidad Federativa - Siempre "Chiapas"
        print("   Llenando entidad federativa...")
        llenar_entidad_federativa(driver)
        
        time.sleep(1)

        # Género
        print("   Seleccionando género...")
        generos = ["Hombre", "Mujer", "No binario", "Prefiero no decirlo"]
        generos_validos = obtener_opciones_validas(generos)
        genero_seleccionado = random.choice(generos_validos)
        click_option(driver, genero_seleccionado)
        print(f"   [OK] Género: {genero_seleccionado}")

        # Nivel de estudios
        print("   Seleccionando nivel de estudios...")
        estudios = [
            "Primaria", "Secundaria", "Preparatoria o bachillerato",
            "Técnico concluido", "Licenciatura trunca", "Licenciatura concluida", "Posgrado"
        ]
        estudios_validos = obtener_opciones_validas(estudios)
        estudio_seleccionado = random.choice(estudios_validos)
        click_option(driver, estudio_seleccionado)
        print(f"   [OK] Estudios: {estudio_seleccionado}")

        # Ocupación
        print("   Seleccionando ocupación...")
        ocupaciones = [
            "Estudiante", "Empleado/a tiempo completo", "Empleado/a medio tiempo o parcial",
            "Empresario/a", "Jubilado/a o pensionado/a", "Desempleado/a", "Trabajo en el hogar",
            "Freelancer"
        ]
        ocupaciones_validas = obtener_opciones_validas(ocupaciones)
        ocupacion_seleccionada = random.choice(ocupaciones_validas)
        click_option(driver, ocupacion_seleccionada)
        print(f"   [OK] Ocupación: {ocupacion_seleccionada}")

        # Ingreso mensual
        print("   Seleccionando ingreso mensual...")
        ingresos = [
            "Menos de $8,000", "Entre $8,000 y $15,000", "Entre $15,001 y $25,000",
            "Entre $25,001 y $35,000", "Más de $35,000", "Prefiero no responder"
        ]
        ingresos_validos = obtener_opciones_validas(ingresos)
        ingreso_seleccionado = random.choice(ingresos_validos)
        click_option(driver, ingreso_seleccionado)
        print(f"   [OK] Ingreso: {ingreso_seleccionado}")

        time.sleep(2)

        # Responder todas las preguntas específicas con la función mejorada
        if not responder_todas_las_preguntas(driver):
            print("   [ERROR] No se pudieron responder todas las preguntas")
            return False

        # Enviar formulario con reintentos automáticos
        print("   Enviando formulario...")
        max_intentos_envio = 5
        
        for intento_envio in range(max_intentos_envio):
            try:
                print(f"   Intento de envío {intento_envio + 1}/{max_intentos_envio}")
                
                # Hacer scroll hasta el final
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Buscar y hacer clic en el botón enviar
                boton_enviar = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[text()="Enviar"]'))
                )
                boton_enviar.click()
                time.sleep(3)  # Esperar a que se procese
                
                # Verificar si el formulario fue enviado exitosamente
                # Buscar indicadores de éxito
                indicadores_exito = [
                    "Se ha registrado tu respuesta",
                    "Tu respuesta se ha registrado",
                    "Gracias por tu respuesta",
                    "Respuesta registrada",
                    "Se registró tu respuesta"
                ]
                
                formulario_enviado = False
                for indicador in indicadores_exito:
                    if len(driver.find_elements(By.XPATH, f"//*[contains(text(), '{indicador}')]")) > 0:
                        print(f"   [OK] Formulario enviado correctamente - Detectado: '{indicador}'")
                        formulario_enviado = True
                        break
                
                # También verificar si la URL cambió (otra señal de éxito)
                if not formulario_enviado:
                    url_actual = driver.current_url
                    if "formResponse" in url_actual or "thanks" in url_actual.lower():
                        print("   [OK] Formulario enviado correctamente - URL de confirmación detectada")
                        formulario_enviado = True
                
                if formulario_enviado:
                    return True
                
                # Si llegamos aquí, el formulario no se envió exitosamente
                # Buscar preguntas sin responder o con errores
                print("   [INFO] El formulario no se envió, buscando preguntas sin responder...")
                
                # Buscar elementos que indiquen errores o preguntas obligatorias
                elementos_error = driver.find_elements(By.XPATH, "//*[contains(@class, 'error') or contains(@class, 'required')]")
                preguntas_faltantes = driver.find_elements(By.XPATH, "//*[contains(text(), 'Esta pregunta es obligatoria') or contains(text(), 'This question is required')]")
                
                if elementos_error or preguntas_faltantes:
                    print(f"   [INFO] Encontradas {len(elementos_error + preguntas_faltantes)} preguntas con problemas")
                    
                    # Hacer scroll hacia arriba para ver las preguntas
                    driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(1)
                    
                    # Intentar encontrar y responder preguntas específicas que faltan
                    preguntas_radio_sin_responder = driver.find_elements(By.XPATH, 
                        "//div[contains(@class, 'required') or contains(@class, 'error')]//div[@role='radio']")
                    
                    if preguntas_radio_sin_responder:
                        print("   [INFO] Respondiendo preguntas de radio faltantes...")
                        # Agrupar por contenedor padre
                        contenedores_procesados = set()
                        for opcion in preguntas_radio_sin_responder:
                            try:
                                # Encontrar el contenedor padre
                                contenedor = opcion
                                for _ in range(10):
                                    contenedor = contenedor.find_element(By.XPATH, '..')
                                    opciones_en_contenedor = contenedor.find_elements(By.XPATH, './/div[@role="radio"]')
                                    if len(opciones_en_contenedor) >= 2:
                                        break
                                
                                contenedor_id = contenedor.get_attribute('outerHTML')[:100]  # ID único
                                if contenedor_id not in contenedores_procesados:
                                    contenedores_procesados.add(contenedor_id)
                                    
                                    # Encontrar opciones válidas (sin "Otro")
                                    opciones_validas = []
                                    for opt in opciones_en_contenedor:
                                        try:
                                            texto_opt = opt.find_element(By.XPATH, './/span').text.lower()
                                            if not any(palabra in texto_opt for palabra in ['otro', 'otra', 'other', 'especifica']):
                                                opciones_validas.append(opt)
                                        except:
                                            opciones_validas.append(opt)
                                    
                                    # Seleccionar una opción válida
                                    if opciones_validas:
                                        opcion_elegida = random.choice(opciones_validas)
                                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", opcion_elegida)
                                        time.sleep(0.5)
                                        
                                        # Intentar hacer clic
                                        try:
                                            opcion_elegida.click()
                                        except:
                                            driver.execute_script("arguments[0].click();", opcion_elegida)
                                        
                                        time.sleep(0.5)
                                        print("   [OK] Pregunta faltante respondida")
                            except:
                                continue
                    
                    # También buscar todas las preguntas de radio sin responder de forma general
                    todas_las_opciones = driver.find_elements(By.XPATH, '//div[@role="radio"]')
                    contenedores_sin_respuesta = []
                    
                    # Agrupar opciones por contenedor padre
                    contenedores_temp = {}
                    for opcion in todas_las_opciones:
                        try:
                            contenedor = opcion
                            for _ in range(8):
                                contenedor = contenedor.find_element(By.XPATH, '..')
                                opciones_en_contenedor = contenedor.find_elements(By.XPATH, './/div[@role="radio"]')
                                if len(opciones_en_contenedor) >= 2:
                                    contenedor_id = id(contenedor)
                                    if contenedor_id not in contenedores_temp:
                                        contenedores_temp[contenedor_id] = contenedor
                                    break
                        except:
                            continue
                    
                    # Verificar cuáles contenedores no tienen respuesta
                    for contenedor_id, contenedor in contenedores_temp.items():
                        try:
                            opciones_marcadas = contenedor.find_elements(By.XPATH, './/div[@role="radio" and @aria-checked="true"]')
                            if not opciones_marcadas:
                                contenedores_sin_respuesta.append(contenedor)
                        except:
                            continue
                    
                    # Responder contenedores sin respuesta
                    if contenedores_sin_respuesta:
                        print(f"   [INFO] Respondiendo {len(contenedores_sin_respuesta)} preguntas adicionales sin responder...")
                        for contenedor in contenedores_sin_respuesta[:5]:  # Limitar a 5 para evitar bucle infinito
                            try:
                                opciones_disponibles = contenedor.find_elements(By.XPATH, './/div[@role="radio"]')
                                opciones_validas = []
                                
                                for opt in opciones_disponibles:
                                    try:
                                        texto_opt = opt.find_element(By.XPATH, './/span').text.lower()
                                        if not any(palabra in texto_opt for palabra in ['otro', 'otra', 'other', 'especifica']):
                                            opciones_validas.append(opt)
                                    except:
                                        opciones_validas.append(opt)
                                
                                if opciones_validas:
                                    opcion_elegida = random.choice(opciones_validas)
                                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", opcion_elegida)
                                    time.sleep(0.5)
                                    
                                    try:
                                        opcion_elegida.click()
                                    except:
                                        driver.execute_script("arguments[0].click();", opcion_elegida)
                                    
                                    time.sleep(0.5)
                                    print("   [OK] Pregunta adicional respondida")
                            except:
                                continue
                
                # Continuar con el siguiente intento de envío
                print("   [INFO] Reintentando envío después de completar preguntas faltantes...")
                time.sleep(2)
                
            except Exception as e:
                print(f"   [ERROR] Error en intento de envío {intento_envio + 1}: {str(e)[:100]}")
                time.sleep(2)
        
        print("   [ERROR] No se pudo enviar el formulario después de múltiples intentos")
        return False

    except Exception as e:
        print(f"   [ERROR] Error general al llenar el formulario: {e}")
        return False
    finally:
        time.sleep(3)
        driver.quit()

# === Bucle principal ===
print("*** Iniciando script de llenado automático de formularios ***")
print(f"- Se enviarán {NUM_RESPUESTAS} respuestas")
print(f"- Tiempo de espera entre envíos: {TIEMPO_MIN}-{TIEMPO_MAX} segundos")
print("- Entidad Federativa: Chiapas (fijo)")
print("-" * 60)

formularios_completados = 0
for i in range(NUM_RESPUESTAS):
    print(f"\n>>> Enviando respuesta {i+1} de {NUM_RESPUESTAS}")
    if llenar_formulario():
        formularios_completados += 1
    else:
        print(">>> Error al completar el formulario, intentando el siguiente...")

    if i < NUM_RESPUESTAS - 1:
        espera = random.randint(TIEMPO_MIN, TIEMPO_MAX)
        print(f">>> Esperando {espera} segundos antes del siguiente envío...")
        time.sleep(espera)

print(f"\n*** Proceso completado! Se enviaron {formularios_completados} de {NUM_RESPUESTAS} formularios correctamente. ***")
print("*** Todas las respuestas incluyeron 'Chiapas' como entidad federativa. ***")