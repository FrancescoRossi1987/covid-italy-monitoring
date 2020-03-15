<div align="center">

# CoVid-19 Italy Monitoring

A script to visualize some statistics and predictions about the CoVid-19 epidemics in Italy
</div>

### Usage
Install Humor Sans font: http://antiyawn.com/uploads/humorsans.html
```shell script
pip install -r requirements.txt
python3 main.py
```


### Example
The script produces the following report:
```
--------------------------------------------------
2020-03-14 Report
--------------------------------------------------
Total number of infected individuals is 21157
Total number of recovered individuals is 1966
Total number of dead individuals is 1441
Total number of tested individuals is 109170
--------------------------------------------------
Current number of infected individuals is 17750
--- hospitalized individuals are 8372
--- hospitalized individuals are ICU is 1518
--- home isolated individuals are 7860
--------------------------------------------------
Number of new infected is 3497
Growth rate is 0.20 (5 days smoothing is 0.18)
--------------------------------------------------
Forecast with the current growth rate (0.20)
--- after 3 days: 36378
--- after 5 days: 52212
--- after 10 days: 128851
--------------------------------------------------
Optimistic forecast (growth rate = 0.15)
--- after 3 days: 32011
--- after 5 days: 42188
--- after 10 days: 84128
--------------------------------------------------
Pessimistic forecast (growth rate = 0.25)
--- after 3 days: 41126
--- after 5 days: 64055
--- after 10 days: 193938
```

and the following images:
![stats][example]
![forecast][forecast]

[example]: example.png
[forecast]: forecast.png
