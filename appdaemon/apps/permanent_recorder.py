import appdaemon.plugins.hass.hassapi as hass
import mysql.connector

# Saves a state or an attribute to a mysql db (like recorder, but less data => permanent)
#
# Args:
# - light_brightness (list of light entities, brightness is saved. on/off lights = 100%/0%)
# - state (list of entities, state is saved)
# - heating_target_temperature (list of climate entities, target temperature is saved)
# - db_passwd

class permanent_recorder(hass.Hass):

    def initialize(self):
        self.log("Permanent Logger started")
        self.mydb = mysql.connector.connect(
            host="core-mariadb",
            user="appdaemon",
            passwd=self.args["db_passwd"],
            database="homeassistant-permanent"
        )
        
        self.init_table()
        self.write_test1()
        self.write_test2()

        

    def init_table(self):
        mycursor = self.mydb.cursor()
        mycursor.execute("SHOW TABLES")
        if "ha" in mycursor:
            self.log("Table ha in database found. Will use it")
        else:
            mycursor.execute("CREATE TABLE ha (id INT AUTO_INCREMENT PRIMARY KEY, domain VARCHAR(255), entity_id VARCHAR(255), value VARCHAR(255), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    
    def write_test1(self):
        mycursor = self.mydb.cursor()
        sql = "INSERT INTO ha (domain, entity_id, value) VALUES (%s, %s, %s)"
        val = ("Test-Domain", "Test-Entity", "on")
        mycursor.execute(sql, val)
        self.mydb.commit()
        
    def write_test2(self):
        mycursor = self.mydb.cursor()
        sql = "INSERT INTO ha (domain, entity_id, value) VALUES (%s, %s, %s)"
        val = ("Test-Domain 2", "Test-Entity 2", 25)
        mycursor.execute(sql, val)
        self.mydb.commit()
