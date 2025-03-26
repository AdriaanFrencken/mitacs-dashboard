## Suggestions for improving data organization
**add these columns:**
  * measurement_type =[I-t, I-V]
  * include GR = [True, False]
  * surface_treatment = [TiO2, CdS, ..]
  * sensor_id

## App features
* Capture raw current and absolute current in data.
* Calculate the mean stable `dark_current_start` and `dark_current_end` 
* Calculate the noise or RMS value of `dark_current_start`, `dark_current_end`, `photocurrent_end`,
* If possible, do a fast fourier transform to extract noise frequencies.
* Add colors or distinct stylings to the dashed vline and hline
