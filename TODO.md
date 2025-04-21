## Suggestions for improving data organization
**add these columns:**
  * measurement_type =[I-t, I-V]
  * include GR = [True, False]
  * surface_treatment = [TiO2, CdS, ..]
  * sensor_id
* Capture raw current and absolute current in data.

## App features
* Calculate the mean stable `dark_current_start` and `dark_current_end` 
* Calculate the noise or RMS value of `dark_current_start`, `dark_current_end`, `photocurrent_end`,
* If possible, do a fast fourier transform to extract noise frequencies.
* Add colors or distinct stylings to the dashed vline and hline

## 2025-04-17
* Combine the Power law and IV app in one page
* Add Power Law analysis for negative IV section
* Add BK8 POR data into default
* Add optional horizontal dashed line at I=0 for all I-t plots


