import appdaemon.plugins.hass.hassapi as hass

#
# Simulate Presence
#
# Args: 
# 

class simulate_presence(hass.Hass):

    def initialize(self):
        # App Status
        if self.get_state("input_boolean.anwesenheit_simulieren") == "on" and self.get_state("binary_sensor.anwesenheit_haus") == "off":
            self.active = True
            self.log("Anwesenheitssiumlation aktiviert")
        else:
            self.active = False
            self.log("Anwesenheitssiumlation deaktiviert")
        self.listen_state("input_boolean.anwesenheit_simulieren", self.app_status_changed)
        self.listen_state("binary_sensor.anwesenheit_haus", self.app_status_changed)
        # Wind Status
        if self.get_state("binary_sensor.windalarm_1") == "on":
            self.windalarm = True
        else:
            self.windalarm = False
        self.listen_state("binary_sensor.windalarm_1", self.wind_status_changed)
        # Monday, Wednesday, Friday morning
        self.run_daily(self.light_off, "06:31:00", constrain_days="mon,wed,fri", light="light.wandwurfel_la")
        self.run_daily(self.light_off, "06:31:30", constrain_days="mon,wed,fri", light="light.wandwurfel_le")
        self.run_daily(self.light_off, "06:34:17", constrain_days="mon,wed,fri", light="light.panels_flur_eg")
        self.run_daily(self.light_on, "06:31:34", constrain_days="mon,wed,fri", light="light.panels_flur_og", brightness=60)
        self.run_daily(self.light_off, "07:34:32", constrain_days="mon,wed,fri", light="light.panels_flur_og")
        self.run_daily(self.light_on, "06:37:21", constrain_days="mon,wed,fri", light="light.panels_bad_og", brightness=40)
        self.run_daily(self.light_off, "07:48:46", constrain_days="mon,wed,fri", light="light.panels_bad_og")
        self.run_daily(self.cover_up, "07:18:49", constrain_days="mon,wed,fri", cover="cover.jalousie_bad_og")
        self.run_daily(self.cover_up, "07:17:56", constrain_days="mon,wed,fri", cover="cover.jalousie_la_bodentiefes")
        self.run_daily(self.cover_up, "07:17:45", constrain_days="mon,wed,fri", cover="cover.jalousie_la_lichtband")
        self.run_daily(self.cover_up, "07:17:05", constrain_days="mon,wed,fri", cover="cover.jalousie_le_bodentiefes")
        self.run_daily(self.cover_up, "07:17:23", constrain_days="mon,wed,fri", cover="cover.jalousie_le_lichtband")
        self.run_daily(self.cover_up, "07:25:49", constrain_days="mon,wed,fri", cover="cover.jalousie_kuche")
        self.run_daily(self.cover_up, "07:25:55", constrain_days="mon,wed,fri", cover="cover.jalousie_hst")
        self.run_daily(self.cover_up, "07:25:37", constrain_days="mon,wed,fri", cover="cover.jalousie_wz_bodentiefes")
        self.run_daily(self.cover_up, "07:25:08", constrain_days="mon,wed,fri", cover="cover.jalousie_wz_couch")
        self.run_daily(self.light_on, "06:14:58", constrain_days="mon,wed,fri", light="light.panels_schlafzimmer", brightness=40)
        self.run_daily(self.light_off, "06:55:23", constrain_days="mon,wed,fri", light="light.panels_schlafzimmer")
        self.run_daily(self.cover_up, "06:56:13", constrain_days="mon,wed,fri", cover="cover.jalousie_schlafzimmer")
        # Monday, Wednesday, Friday evening
        self.run_daily(self.light_on, "18:31:45", constrain_days="mon,wed,fri", light="light.panels_flur_og", brightness=45)
        self.run_daily(self.light_off, "19:44:28", constrain_days="mon,wed,fri", light="light.panels_flur_og")
        self.run_daily(self.light_on, "18:37:17", constrain_days="mon,wed,fri", light="light.panels_bad_og", brightness=40)
        self.run_daily(self.light_off, "19:18:56", constrain_days="mon,wed,fri", light="light.panels_bad_og")
        self.run_daily(self.cover_down, "19:25:34", constrain_days="mon,wed,fri", cover="cover.jalousie_la_bodentiefes")
        self.run_daily(self.cover_down, "19:25:44", constrain_days="mon,wed,fri", cover="cover.jalousie_la_lichtband")
        self.run_daily(self.light_on, "19:26:48", constrain_days="mon,wed,fri", light="light.panels_la", brightness=40)
        self.run_daily(self.light_off, "19:36:04", constrain_days="mon,wed,fri", light="light.panels_la")
        self.run_daily(self.light_on, "19:36:16", constrain_days="mon,wed,fri", light="light.wandwurfel_la", brightness=3)
        self.run_daily(self.cover_down, "19:25:38", constrain_days="mon,wed,fri", cover="cover.jalousie_le_bodentiefes")
        self.run_daily(self.cover_down, "19:25:30", constrain_days="mon,wed,fri", cover="cover.jalousie_le_lichtband")
        self.run_daily(self.light_on, "19:26:00", constrain_days="mon,wed,fri", light="light.panels_le", brightness=40)
        self.run_daily(self.light_off, "19:38:34", constrain_days="mon,wed,fri", light="light.panels_le")
        self.run_daily(self.light_on, "19:38:57", constrain_days="mon,wed,fri", light="light.wandwurfel_le", brightness=3)
        self.run_daily(self.light_on, "19:14:59", constrain_days="mon,wed,fri", light="light.panels_schlafzimmer", brightness=30)
        self.run_daily(self.light_off, "19:55:51", constrain_days="mon,wed,fri", light="light.panels_schlafzimmer")
        self.run_daily(self.light_on, "18:04:49", constrain_days="mon,wed,fri", light="light.panels_flur_eg", brightness=30)
        self.run_daily(self.light_off, "22:34:46", constrain_days="mon,wed,fri", light="light.panels_flur_eg")
        self.run_daily(self.cover_down, "18:25:23", constrain_days="mon,wed,fri", cover="cover.jalousie_kuche")
        self.run_daily(self.cover_down, "18:25:01", constrain_days="mon,wed,fri", cover="cover.jalousie_hst")
        self.run_daily(self.cover_down, "18:25:02", constrain_days="mon,wed,fri", cover="cover.jalousie_wz_bodentiefes")
        self.run_daily(self.cover_down, "18:25:03", constrain_days="mon,wed,fri", cover="cover.jalousie_wz_couch")
        self.run_daily(self.light_on, "19:55:07", constrain_days="mon,wed,fri", light="light.wandleuchten_esszimmer_gemutlich", brightness=60)
        self.run_daily(self.light_off, "22:26:09", constrain_days="mon,wed,fri", light="light.wandleuchten_esszimmer_gemutlich")
        self.run_daily(self.light_on, "19:58:13", constrain_days="mon,wed,fri", light="light.schrankbeleuchtung_wohnzimmer", brightness=50)
        self.run_daily(self.light_off, "22:24:47", constrain_days="mon,wed,fri", light="light.schrankbeleuchtung_wohnzimmer")
        self.run_daily(self.light_on, "23:04:24", constrain_days="mon,wed,fri", light="light.panels_flur_eg", brightness=10)
        # Tuesday, Thursday, Saturday morning
        self.run_daily(self.light_off, "06:21:46", constrain_days="tue,thu,sat", light="light.wandwurfel_la")
        self.run_daily(self.light_off, "06:21:23", constrain_days="tue,thu,sat", light="light.wandwurfel_le")
        self.run_daily(self.light_off, "06:29:43", constrain_days="tue,thu,sat", light="light.panels_flur_eg")
        self.run_daily(self.light_on, "06:22:58", constrain_days="tue,thu,sat", light="light.panels_flur_og", brightness=60)
        self.run_daily(self.light_off, "07:39:26", constrain_days="tue,thu,sat", light="light.panels_flur_og")
        self.run_daily(self.light_on, "06:24:46", constrain_days="tue,thu,sat", light="light.panels_bad_og", brightness=40)
        self.run_daily(self.light_off, "07:27:59", constrain_days="tue,thu,sat", light="light.panels_bad_og")
        self.run_daily(self.cover_up, "07:11:04", constrain_days="tue,thu,sat", cover="cover.jalousie_bad_og")
        self.run_daily(self.cover_up, "07:08:06", constrain_days="tue,thu,sat", cover="cover.jalousie_la_bodentiefes")
        self.run_daily(self.cover_up, "07:08:01", constrain_days="tue,thu,sat", cover="cover.jalousie_la_lichtband")
        self.run_daily(self.cover_up, "07:08:27", constrain_days="tue,thu,sat", cover="cover.jalousie_le_bodentiefes")
        self.run_daily(self.cover_up, "07:08:38", constrain_days="tue,thu,sat", cover="cover.jalousie_le_lichtband")
        self.run_daily(self.cover_up, "07:19:35", constrain_days="tue,thu,sat", cover="cover.jalousie_kuche")
        self.run_daily(self.cover_up, "07:19:01", constrain_days="tue,thu,sat", cover="cover.jalousie_hst")
        self.run_daily(self.cover_up, "07:19:02", constrain_days="tue,thu,sat", cover="cover.jalousie_wz_bodentiefes")
        self.run_daily(self.cover_up, "07:19:03", constrain_days="tue,thu,sat", cover="cover.jalousie_wz_couch")
        self.run_daily(self.light_on, "06:16:05", constrain_days="tue,thu,sat", light="light.panels_schlafzimmer", brightness=40)
        self.run_daily(self.light_off, "06:47:47", constrain_days="tue,thu,sat", light="light.panels_schlafzimmer")
        self.run_daily(self.cover_up, "06:48:54", constrain_days="tue,thu,sat", cover="cover.jalousie_schlafzimmer")
        # Tuesday, Thursday, Saturday evening
        self.run_daily(self.light_on, "18:25:38", constrain_days="tue,thu,sat", light="light.panels_flur_og", brightness=45)
        self.run_daily(self.light_off, "19:53:35", constrain_days="tue,thu,sat", light="light.panels_flur_og")
        self.run_daily(self.light_on, "18:33:25", constrain_days="tue,thu,sat", light="light.panels_bad_og", brightness=40)
        self.run_daily(self.light_off, "19:06:33", constrain_days="tue,thu,sat", light="light.panels_bad_og")
        self.run_daily(self.cover_down, "19:04:55", constrain_days="tue,thu,sat", cover="cover.jalousie_la_bodentiefes")
        self.run_daily(self.cover_down, "19:04:44", constrain_days="tue,thu,sat", cover="cover.jalousie_la_lichtband")
        self.run_daily(self.light_on, "19:05:22", constrain_days="tue,thu,sat", light="light.panels_la", brightness=40)
        self.run_daily(self.light_off, "19:24:11", constrain_days="tue,thu,sat", light="light.panels_la")
        self.run_daily(self.light_on, "19:24:23", constrain_days="tue,thu,sat", light="light.wandwurfel_la", brightness=3)
        self.run_daily(self.cover_down, "19:05:30", constrain_days="tue,thu,sat", cover="cover.jalousie_le_bodentiefes")
        self.run_daily(self.cover_down, "19:05:47", constrain_days="tue,thu,sat", cover="cover.jalousie_le_lichtband")
        self.run_daily(self.light_on, "19:06:37", constrain_days="tue,thu,sat", light="light.panels_le", brightness=40)
        self.run_daily(self.light_off, "19:28:00", constrain_days="tue,thu,sat", light="light.panels_le")
        self.run_daily(self.light_on, "19:29:01", constrain_days="tue,thu,sat", light="light.wandwurfel_le", brightness=3)
        self.run_daily(self.light_on, "19:28:03", constrain_days="tue,thu,sat", light="light.panels_schlafzimmer", brightness=30)
        self.run_daily(self.light_off, "19:59:23", constrain_days="tue,thu,sat", light="light.panels_schlafzimmer")
        self.run_daily(self.light_on, "18:16:16", constrain_days="tue,thu,sat", light="light.panels_flur_eg", brightness=30)
        self.run_daily(self.light_off, "22:23:00", constrain_days="tue,thu,sat", light="light.panels_flur_eg")
        self.run_daily(self.cover_down, "18:14:36", constrain_days="tue,thu,sat", cover="cover.jalousie_kuche")
        self.run_daily(self.cover_down, "18:14:01", constrain_days="tue,thu,sat", cover="cover.jalousie_hst")
        self.run_daily(self.cover_down, "18:14:02", constrain_days="tue,thu,sat", cover="cover.jalousie_wz_bodentiefes")
        self.run_daily(self.cover_down, "18:14:03", constrain_days="tue,thu,sat", cover="cover.jalousie_wz_couch")
        self.run_daily(self.light_on, "19:47:05", constrain_days="tue,thu,sat", light="light.wandleuchten_esszimmer_gemutlich", brightness=60)
        self.run_daily(self.light_off, "22:22:15", constrain_days="tue,thu,sat", light="light.wandleuchten_esszimmer_gemutlich")
        self.run_daily(self.light_on, "19:51:25", constrain_days="tue,thu,sat", light="light.schrankbeleuchtung_wohnzimmer", brightness=50)
        self.run_daily(self.light_off, "22:21:35", constrain_days="tue,thu,sat", light="light.schrankbeleuchtung_wohnzimmer")
        self.run_daily(self.light_on, "22:54:55", constrain_days="tue,thu,sat", light="light.panels_flur_eg", brightness=10)
        # Sunday morning
        self.run_daily(self.light_off, "06:51:47", constrain_days="sun", light="light.wandwurfel_la")
        self.run_daily(self.light_off, "06:51:27", constrain_days="sun", light="light.wandwurfel_le")
        self.run_daily(self.light_off, "06:54:37", constrain_days="sun", light="light.panels_flur_eg")
        self.run_daily(self.light_on, "06:51:28", constrain_days="sun", light="light.panels_flur_og", brightness=60)
        self.run_daily(self.light_off, "07:54:08", constrain_days="sun", light="light.panels_flur_og")
        self.run_daily(self.light_on, "06:57:17", constrain_days="sun", light="light.panels_bad_og", brightness=40)
        self.run_daily(self.light_off, "07:58:47", constrain_days="sun", light="light.panels_bad_og")
        self.run_daily(self.cover_up, "07:58:44", constrain_days="sun", cover="cover.jalousie_bad_og")
        self.run_daily(self.cover_up, "07:37:46", constrain_days="sun", cover="cover.jalousie_la_bodentiefes")
        self.run_daily(self.cover_up, "07:37:41", constrain_days="sun", cover="cover.jalousie_la_lichtband")
        self.run_daily(self.cover_up, "07:37:24", constrain_days="sun", cover="cover.jalousie_le_bodentiefes")
        self.run_daily(self.cover_up, "07:37:46", constrain_days="sun", cover="cover.jalousie_le_lichtband")
        self.run_daily(self.cover_up, "07:43:53", constrain_days="sun", cover="cover.jalousie_kuche")
        self.run_daily(self.cover_up, "07:43:41", constrain_days="sun", cover="cover.jalousie_hst")
        self.run_daily(self.cover_up, "07:43:50", constrain_days="sun", cover="cover.jalousie_wz_bodentiefes")
        self.run_daily(self.cover_up, "07:43:20", constrain_days="sun", cover="cover.jalousie_wz_couch")
        self.run_daily(self.light_on, "06:54:10", constrain_days="sun", light="light.panels_schlafzimmer", brightness=40)
        self.run_daily(self.light_off, "07:37:40", constrain_days="sun", light="light.panels_schlafzimmer")
        self.run_daily(self.cover_up, "07:37:00", constrain_days="sun", cover="cover.jalousie_schlafzimmer")
        # Sunday evening
        self.run_daily(self.light_on, "18:41:34", constrain_days="sun", light="light.panels_flur_og", brightness=45)
        self.run_daily(self.light_off, "19:54:21", constrain_days="sun", light="light.panels_flur_og")
        self.run_daily(self.light_on, "19:47:11", constrain_days="sun", light="light.panels_bad_og", brightness=40)
        self.run_daily(self.light_off, "19:58:10", constrain_days="sun", light="light.panels_bad_og")
        self.run_daily(self.cover_down, "19:27:47", constrain_days="sun", cover="cover.jalousie_la_bodentiefes")
        self.run_daily(self.cover_down, "19:27:39", constrain_days="sun", cover="cover.jalousie_la_lichtband")
        self.run_daily(self.light_on, "19:28:34", constrain_days="sun", light="light.panels_la", brightness=40)
        self.run_daily(self.light_off, "19:43:58", constrain_days="sun", light="light.panels_la")
        self.run_daily(self.light_on, "19:42:43", constrain_days="sun", light="light.wandwurfel_la", brightness=3)
        self.run_daily(self.cover_down, "19:28:30", constrain_days="sun", cover="cover.jalousie_le_bodentiefes")
        self.run_daily(self.cover_down, "19:28:46", constrain_days="sun", cover="cover.jalousie_le_lichtband")
        self.run_daily(self.light_on, "19:29:49", constrain_days="sun", light="light.panels_le", brightness=40)
        self.run_daily(self.light_off, "19:52:43", constrain_days="sun", light="light.panels_le")
        self.run_daily(self.light_on, "19:51:32", constrain_days="sun", light="light.wandwurfel_le", brightness=3)
        self.run_daily(self.light_on, "19:54:21", constrain_days="sun", light="light.panels_schlafzimmer", brightness=30)
        self.run_daily(self.light_off, "20:19:20", constrain_days="sun", light="light.panels_schlafzimmer")
        self.run_daily(self.light_on, "18:34:40", constrain_days="sun", light="light.panels_flur_eg", brightness=30)
        self.run_daily(self.light_off, "23:08:50", constrain_days="sun", light="light.panels_flur_eg")
        self.run_daily(self.cover_down, "18:57:55", constrain_days="sun", cover="cover.jalousie_kuche")
        self.run_daily(self.cover_down, "18:57:01", constrain_days="sun", cover="cover.jalousie_hst")
        self.run_daily(self.cover_down, "18:57:02", constrain_days="sun", cover="cover.jalousie_wz_bodentiefes")
        self.run_daily(self.cover_down, "18:57:03", constrain_days="sun", cover="cover.jalousie_wz_couch")
        self.run_daily(self.light_on, "19:48:25", constrain_days="sun", light="light.wandleuchten_esszimmer_gemutlich", brightness=60)
        self.run_daily(self.light_off, "23:06:35", constrain_days="sun", light="light.wandleuchten_esszimmer_gemutlich")
        self.run_daily(self.light_on, "19:46:45", constrain_days="sun", light="light.schrankbeleuchtung_wohnzimmer", brightness=50)
        self.run_daily(self.light_off, "22:59:07", constrain_days="sun", light="light.schrankbeleuchtung_wohnzimmer")
        self.run_daily(self.light_on, "23:07:28", constrain_days="sun", light="light.panels_flur_eg", brightness=10)

    def app_status_changed(self, entity, attribute, old, new, kwargs):
        if self.get_state("input_boolean.anwesenheit_simulieren") == "on" and self.get_state("binary_sensor.anwesenheit_haus") == "off":
            self.active = True
            self.log("Anwesenheitssiumlation aktiviert")
        else:
            self.active = False
            self.log("Anwesenheitssiumlation deaktiviert")
            if entity == "binary_sensor.anwesenheit_simulieren" and new == "off" and self.get_state("binary_sensor.anwesenheit_haus") == "off":
                self.turn_off("light.panels_flur_og")
                self.turn_off("light.panels_bad_og")
                self.turn_off("light.panels_schlafzimmer")
                self.turn_off("light.panels_la")
                self.turn_off("light.wandwurfel_la")
                self.turn_off("light.panels_le")
                self.turn_off("light.wandwurfel_le")
                self.turn_off("light.panels_flur_eg")
                self.turn_off("light.wandleuchten_esszimmer_gemutlich")
                self.turn_off("light.schrankbeleuchtung_wohnzimmer")

    def wind_status_changed(self, entity, attribute, old, new, kwargs):
        if new == "on":
            self.windalarm = True
            if self.active:
                self.call_service("cover/set_cover_position", entity_id = "cover.jalousie_bad_og", position = 0)
                self.call_service("cover/set_cover_position", entity_id = "cover.jalousie_schlafzimmer", position = 0)
                self.call_service("cover/set_cover_position", entity_id = "cover.jalousie_la_bodentiefes", position = 0)
                self.call_service("cover/set_cover_position", entity_id = "cover.jalousie_la_lichtband", position = 0)
                self.call_service("cover/set_cover_position", entity_id = "cover.jalousie_le_bodentiefes", position = 0)
                self.call_service("cover/set_cover_position", entity_id = "cover.jalousie_le_lichtband", position = 0)
                self.call_service("cover/set_cover_position", entity_id = "cover.jalousie_kuche", position = 0)
                self.call_service("cover/set_cover_position", entity_id = "cover.jalousie_hst", position = 0)
                self.call_service("cover/set_cover_position", entity_id = "cover.jalousie_wz_bodentiefes", position = 0)
                self.call_service("cover/set_cover_position", entity_id = "cover.jalousie_wz_couch", position = 0)
        else:
            self.windalarm = False


    def light_on(self, kwargs):
        if self.active:
            self.turn_on(kwargs["light"], brightness=self.pct_to_byte(self.basic_brightness))

    def light_off(self, kwargs):
        if self.active:
            self.turn_off(kwargs["light"])
    
    def cover_up(self, kwargs):
        if self.active:
            self.call_service("cover/set_cover_position", entity_id = kwargs["cover"], position = 0)
        
    def cover_down(self, kwargs):
        if self.active:
            if not self.windalarm:
                self.call_service("cover/set_cover_position", entity_id = kwargs["cover"], position = 100)

    def pct_to_byte(self, val_pct):
        return float(round(val_pct*255/100))
    
    def byte_to_pct(self, val_byte):
        return float(round(val_byte*100/255))
