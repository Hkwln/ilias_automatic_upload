# ilias_automatic_upload

## what the program should do:
- you give your username an password to the id.txt file
- you upload your pdf to the upload folder
- you run the python script
-  it detects the new uploaded file and automaticly uploads it to the right ilias group submission
-  e.g you upload math exercise 7 it automaticaly uploads to the exercise 7 and if you upload the file theoretical Informatics exercise 3 it should upload there
-  else it should give you an error an redirect you to the page the error occures
-  

## html snipped of the login:
<input id="il_ui_fw_68511f988493f0_23111494" type="text" name="login_form/input_3/input_4" class="form-control form-control-sm">
<input id="il_ui_fw_685127cb954e82_42206210" type="password" name="login_form/input_3/input_5" class="form-control form-control-sm" autocomplete="off">
<button class="btn btn-default" data-action="">Anmelden</button>
for math:
Mathematik für Informatikstudiengänge II (Gruppenübungen) -> Gruppe 05 -> Abgabe zu übungsblätter -> Abgabe Blatt X -> Button:<button class="btn btn-default" data-action="ilias.php?baseClass=ilexercisehandlergui&amp;cmdNode=cn:ns:4m:cd:cc&amp;cmdClass=ilExSubmissionFileGUI&amp;cmd=submissionScreen&amp;ref_id=4110417&amp;from_overview=1&amp;ass_id=118928" id="il_ui_fw_685126129426c3_28930795">Datei abgeben</button>
-> Datei Hochladen Button: <button class="btn btn-default" data-action="ilias.php?baseClass=ilexercisehandlergui&amp;cmdNode=cn:ns:4m:cd:cc&amp;cmdClass=ilExSubmissionFileGUI&amp;cmd=uploadForm&amp;ref_id=4110417&amp;ass_id=118928&amp;from_overview=1" id="il_ui_fw_6851269d1a4485_00537671">Datei hochladen</button>
-> Datei Wählen Button: <button class="btn btn-link dz-clickable" data-action="#" id="il_ui_fw_685126bea236d3_42829388">Dateien wählen</button>
-> wait a short time, it takes time to upload the file, then Speichern:
<button class="btn btn-default" data-action="">Speichern</button>




using: python, watchdog, selenium
