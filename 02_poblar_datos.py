import os
import time
import random
from datetime import date, timedelta, time as dt_time
from faker import Faker
from sqlalchemy import create_engine, text

fake = Faker(['es_CL', 'es_ES'])
random.seed(42)
Faker.seed(42)

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "rootpassword")
DB_NAME = os.getenv("DB_NAME", "turismo_astronomico")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def esperar_mysql(max_intentos=20):
    for intento in range(1, max_intentos + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            print(f"Esperando a que MySQL acepte conexiones ({intento}/{max_intentos})...")
            time.sleep(3)
    raise RuntimeError("No se pudo conectar a MySQL tras múltiples intentos.")

def poblar():
    esperar_mysql()
    with engine.begin() as conn:
        count_centros = conn.execute(text("SELECT COUNT(*) FROM Centro_astronomico")).scalar()
        if count_centros > 0:
            print("La base de datos ya contiene registros iniciales.")
            return

        # 1. Roles
        conn.execute(text("""
            INSERT INTO Roles (codigo_rol, nombre_rol) VALUES
            ('ROL01', 'admin'),
            ('ROL02', 'operador')
        """))

        # 2. Centros Astronómicos
        centros = [
            ('C01', 'Observatorio Valle del Elqui', 'Vicuña, Región de Coquimbo', 180, 1),
            ('C02', 'Centro Astronómico Atacama Sur', 'San Pedro de Atacama, Antofagasta', 220, 1),
            ('C03', 'Observatorio Cerro Tololo Divulgación', 'Paihuano, Región de Coquimbo', 150, 1),
            ('C04', 'Complejo Astronómico Cajón del Maipo', 'San José de Maipo, RM', 140, 1),
            ('C05', 'Observatorio Cruz del Sur', 'Combarbalá, Región de Coquimbo', 160, 1),
        ]
        for c in centros:
            conn.execute(text("""
                INSERT INTO Centro_astronomico (codigo_centro, nombre, ubicacion, capacidad_maxima, activo)
                VALUES (:c0, :c1, :c2, :c3, :c4)
            """), {"c0": c[0], "c1": c[1], "c2": c[2], "c3": c[3], "c4": c[4]})

        # 3. Zonas de Observación
        zonas = []
        for idx, c in enumerate(centros, start=1):
            for z_num in range(1, 4):
                z_code = f"Z{idx:02d}{z_num}"
                zonas.append((z_code, c[0]))
                conn.execute(text("""
                    INSERT INTO Zonas_observacion (codigo_zona, codigo_centro, nombre_zona, indice_oscuridad, altitud_msnm, capacidad_zona)
                    VALUES (:z0, :z1, :z2, :z3, :z4, :z5)
                """), {
                    "z0": z_code,
                    "z1": c[0],
                    "z2": f"Cúpula / Terraza {z_num} - {c[1].split()[1]}",
                    "z3": round(random.uniform(19.5, 21.9), 2),
                    "z4": random.randint(950, 2600),
                    "z5": random.randint(25, 60)
                })

        # 4. Equipamiento y Calibraciones
        equipos = []
        for i in range(1, 21):
            eq_code = f"EQ{i:03d}"
            c_code = random.choice(centros)[0]
            equipos.append(eq_code)
            conn.execute(text("""
                INSERT INTO Equipamiento (codigo_equipo, codigo_centro, nombre_equipo, tipo_equipo, estado_operativo, fecha_adquisicion)
                VALUES (:e0, :e1, :e2, :e3, :e4, :e5)
            """), {
                "e0": eq_code,
                "e1": c_code,
                "e2": f"Telescopio Celestron C{random.choice([8, 11, 14])}-HD #{i}",
                "e3": random.choice(["Reflector", "Refractor", "Catadióptrico", "Solar H-Alfa"]),
                "e4": "Operativo",
                "e5": fake.date_between(start_date="-4y", end_date="-6m")
            })
            conn.execute(text("""
                INSERT INTO Calibraciones (codigo_calibracion, codigo_equipo, fecha_calibracion, resultado, observaciones_tecnicas)
                VALUES (:cal0, :cal1, :cal2, :cal3, :cal4)
            """), {
                "cal0": f"CAL{i:04d}",
                "cal1": eq_code,
                "cal2": fake.date_between(start_date="-6m", end_date="today"),
                "cal3": "Aprobada",
                "cal4": "Colimación óptica y seguimiento sideral verificados."
            })

        # 5. Personal, Especializaciones y Cuentas de Usuario
        guias = []
        for i in range(1, 25):
            p_code = f"P{i:03d}"
            c_code = random.choice(centros)[0]
            rol_code = "ROL01" if i <= 2 else "ROL02"
            conn.execute(text("""
                INSERT INTO Personal (codigo_personal, codigo_centro, codigo_rol, rut, nombre_completo, correo, telefono, fecha_contratacion, activo)
                VALUES (:p0, :p1, :p2, :p3, :p4, :p5, :p6, :p7, 1)
            """), {
                "p0": p_code,
                "p1": c_code,
                "p2": rol_code,
                "p3": f"{random.randint(12000000, 22999999)}-{random.randint(0, 9)}",
                "p4": fake.name(),
                "p5": f"staff{i}@turismoastronomico.cl",
                "p6": f"+569{random.randint(10000000, 99999999)}",
                "p7": fake.date_between(start_date="-5y", end_date="-3m")
            })

            if i <= 6:
                conn.execute(text("INSERT INTO Investigadores VALUES (:p, :esp, :gr, :pub)"), {
                    "p": p_code, "esp": random.choice(["Astrofísica Estelar", "Cosmología", "Física Solar"]),
                    "gr": "Doctorado", "pub": random.randint(4, 28)
                })
            elif i <= 12:
                conn.execute(text("INSERT INTO Tecnicos VALUES (:p, :area, :cert)"), {
                    "p": p_code, "area": "Óptica y Monturas Ecuatoriales", "cert": f"CERT-OPT-{i:02d}"
                })
            elif i <= 20:
                guias.append(p_code)
                conn.execute(text("INSERT INTO Guias_cientificos VALUES (:p, :idi, :exp)"), {
                    "p": p_code, "idi": "Español, Inglés", "exp": random.randint(2, 12)
                })
            else:
                conn.execute(text("INSERT INTO Administrativos VALUES (:p, :cargo, :dep)"), {
                    "p": p_code, "cargo": "Coordinador Operativo", "dep": "Operaciones y Reservas"
                })

        conn.execute(text("""
            INSERT INTO Cuentas_usuarios (nombre_usuario, codigo_personal, contrasena, activo) VALUES
            ('admin', 'P001', 'admin123', 1),
            ('operador', 'P003', 'oper123', 1)
        """))

        # 6. Fenómenos Astronómicos y Subclases
        fenomenos_data = [
            ('F001', 'Manchas Solares Activas AR38', 'Grupo de manchas fotosféricas visibles con filtro H-Alfa', 'Alta', 'Solar'),
            ('F002', 'Prominencias Coronales', 'Eyecciones de plasma en el limbo solar', 'Media', 'Solar'),
            ('F003', 'Luna Gibosa Creciente', 'Observación detallada de cráteres Tycho y Copernicus', 'Alta', 'Lunar'),
            ('F004', 'Eclipse Penumbral de Luna', 'Oscurecimiento parcial del disco lunar', 'Alta', 'Lunar'),
            ('F005', 'Nebulosa de Orión (M42)', 'Región de formación estelar en la espada de Orión', 'Alta', 'Espacio'),
            ('F006', 'Cúmulo Joyero (NGC 4755)', 'Cúmulo abierto en la constelación Cruz del Sur', 'Alta', 'Espacio'),
            ('F007', 'Galaxia del Sombrero (M104)', 'Galaxia espiral con prominente banda de polvo', 'Media', 'Espacio'),
            ('F008', 'Nebulosa de la Tarántula', 'Región H II en la Gran Nube de Magallanes', 'Alta', 'Espacio'),
        ]
        for f_code, f_nom, f_desc, f_vis, f_tipo in fenomenos_data:
            conn.execute(text("""
                INSERT INTO Fenomenos (codigo_fenomeno, nombre_fenomeno, descripcion, visibilidad_estimada, activo)
                VALUES (:f0, :f1, :f2, :f3, 1)
            """), {"f0": f_code, "f1": f_nom, "f2": f_desc, "f3": f_vis})

            if f_tipo == 'Solar':
                conn.execute(text("INSERT INTO Fenomenos_solares VALUES (:f, 'Actividad Fotosférica', 'Moderada')"), {"f": f_code})
            elif f_tipo == 'Lunar':
                conn.execute(text("INSERT INTO Fenomenos_lunares VALUES (:f, 'Gibosa Creciente', 78.50)"), {"f": f_code})
            else:
                conn.execute(text("INSERT INTO Fenomenos_espacios_profundos VALUES (:f, 'Objeto Cielo Profundo', 4.80, 'Cruz del Sur / Orión')"), {"f": f_code})

        # 7. Visitantes y Teléfonos
        visitantes = []
        for i in range(1, 131):
            v_code = f"V{i:03d}"
            visitantes.append(v_code)
            conn.execute(text("""
                INSERT INTO Visitantes (codigo_visitante, rut_pasaporte, nombre, apellido, correo, pais_origen, fecha_nacimiento)
                VALUES (:v0, :v1, :v2, :v3, :v4, :v5, :v6)
            """), {
                "v0": v_code,
                "v1": f"DOC-{100000 + i}",
                "v2": fake.first_name(),
                "v3": fake.last_name(),
                "v4": f"visitante{i}@correo.com",
                "v5": random.choice(["Chile", "Argentina", "Brasil", "España", "Estados Unidos", "Francia"]),
                "v6": fake.date_of_birth(minimum_age=18, maximum_age=72)
            })
            conn.execute(text("INSERT INTO Telefonos_visitantes VALUES (:v, :t)"), {
                "v": v_code, "t": f"+569{random.randint(40000000, 99999999)}"
            })

        # 8. Actividades
        modalidades = ['Observación Nocturna', 'Observación Solar', 'Astrofotografía', 'Charla y Telescopio']
        actividades = []
        for i in range(1, 181):
            ac_code = f"AC{i:03d}"
            z_code, c_code = random.choice(zonas)
            g_code = random.choice(guias)
            mod = random.choice(modalidades)
            fecha_act = fake.date_between(start_date="-10m", end_date="+2m")
            precio = random.choice([18000, 25000, 32000, 45000])
            actividades.append((ac_code, fecha_act))

            conn.execute(text("""
                INSERT INTO Actividad (codigo_actividad, codigo_centro, codigo_zona, codigo_guia, fecha, hora_inicio, hora_fin, modalidad, cupos_disponibles, precio, estado_actividad)
                VALUES (:a0, :a1, :a2, :a3, :a4, :a5, :a6, :a7, :a8, :a9, :a10)
            """), {
                "a0": ac_code, "a1": c_code, "a2": z_code, "a3": g_code,
                "a4": fecha_act,
                "a5": dt_time(11, 0) if mod == 'Observación Solar' else dt_time(21, 30),
                "a6": dt_time(13, 0) if mod == 'Observación Solar' else dt_time(23, 30),
                "a7": mod,
                "a8": random.randint(15, 40),
                "a9": precio,
                "a10": "Realizada" if fecha_act <= date.today() else "Programada"
            })

            f_sel = random.sample([x[0] for x in fenomenos_data], k=random.randint(1, 2))
            for fc in f_sel:
                conn.execute(text("INSERT INTO Actividad_fenomeno VALUES (:a, :f)"), {"a": ac_code, "f": fc})
            eq_sel = random.sample(equipos, k=random.randint(1, 2))
            for ec in eq_sel:
                conn.execute(text("INSERT INTO Actividad_equipamiento VALUES (:a, :e)"), {"a": ac_code, "e": ec})

        # 9. Reservas y Evaluaciones
        res_num = 1
        for ac_code, fecha_act in actividades:
            vis_grupo = random.sample(visitantes, k=random.randint(3, 8))
            eval_corr = 1
            for vc in vis_grupo:
                r_code = f"RE{res_num:04d}"
                res_num += 1
                es_pasada = fecha_act <= date.today()
                asistio = 1 if (es_pasada and random.random() < 0.85) else 0
                estado_res = "Completada" if asistio == 1 else ("Cancelada" if (es_pasada and random.random() < 0.3) else "Confirmada")
                f_res = fecha_act - timedelta(days=random.randint(1, 15))

                conn.execute(text("""
                    INSERT INTO Reservas (codigo_reserva, codigo_actividad, codigo_visitante, fecha_reserva, asistencia_efectiva, observaciones, estado)
                    VALUES (:r0, :r1, :r2, :r3, :r4, :r5, :r6)
                """), {
                    "r0": r_code, "r1": ac_code, "r2": vc, "r3": f_res,
                    "r4": asistio, "r5": fake.sentence(nb_words=4) if random.random() < 0.4 else "",
                    "r6": estado_res
                })

                if asistio == 1 and random.random() < 0.7:
                    conn.execute(text("""
                        INSERT INTO Evaluaciones (codigo_actividad, numero_correlativo, puntuacion_general, calidad_explicacion, calidad_instrumental, comentario, fecha_evaluacion)
                        VALUES (:e0, :e1, :e2, :e3, :e4, :e5, :e6)
                    """), {
                        "e0": ac_code, "e1": eval_corr,
                        "e2": random.randint(4, 5), "e3": random.randint(4, 5), "e4": random.randint(3, 5),
                        "e5": "Excelente experiencia astronómica y explicación del guía.",
                        "e6": fecha_act
                    })
                    eval_corr += 1

    print("Base de datos poblada exitosamente.")

if __name__ == "__main__":
    poblar()
