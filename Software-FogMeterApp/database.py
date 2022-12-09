import sqlite3


def new_patient(dni, pwd, nom, mail, ed, sex, diag, data_ang, data_acc):
    conn = sqlite3.connect('FM.db', timeout=10)
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS pacientes(Dni TEXT, Pwd TEXT,Nom TEXT,Mail TEXT,Ed TEXT,Sex TEXT,Diag TEXT,Data_ang TEXT,Data_acc TEXT)")
    conn.commit()

    conn.execute("INSERT INTO pacientes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (dni,
                 pwd, nom, mail, ed, sex, diag, data_ang, data_acc))
    conn.commit()
    conn.close()


def patient_info(dni):
    conn = sqlite3.connect('FM.db', timeout=10)
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS pacientes(Dni TEXT, Pwd TEXT,Nom TEXT,Mail TEXT,Ed TEXT,Sex TEXT,Diag TEXT,Data_ang TEXT,Data_acc TEXT)")
    conn.commit()

    cursor.execute("SELECT * FROM pacientes WHERE Dni = ?", (dni,))
    resultado = cursor.fetchone()
    conn.commit()
    conn.close()
    return resultado
    # si no está registrado resultado = None

# introducir los nuevos datos


def edit_patient(dni, pwd, nom, mail, ed, sex, diag, data_ang, data_acc):
    conn = sqlite3.connect('FM.db', timeout=10)
    cursor = conn.cursor()

    cursor.execute("UPDATE pacientes SET Pwd = ?, Nom = ?, Mail = ?, Ed = ?, Sex = ?, Diag = ?, Data_ang = ?, Data_acc= ? WHERE Dni = ?",
                   (pwd, nom, mail, ed, sex, diag, data_ang, data_acc, dni))

    conn.commit()
    conn.close()
