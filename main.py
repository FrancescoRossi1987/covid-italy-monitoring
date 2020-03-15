import json
import math
import pathlib
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import requests


def moving_average(a: np.array, n: int = 3) -> np.array:
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n


if __name__ == '__main__':
    raw_data = requests.get('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json'
                            '/dpc-covid19-ita-andamento-nazionale.json')
    if raw_data.status_code != 200:
        raise FileNotFoundError('File not found. Check data URL.')
    try:
        data = raw_data.json()
    except json.decoder.JSONDecodeError:
        decoded_data = raw_data.content.decode('utf-8-sig')
        data = json.loads(decoded_data)

    dates = [datetime.strptime(d['data'][:10], '%Y-%m-%d') for d in data]
    infected_list = [d['totale_casi'] for d in data]
    recovered = np.array([d['dimessi_guariti'] for d in data], dtype=np.int32)
    dead = np.array([d['deceduti'] for d in data], dtype=np.int32)
    hospitalized = np.array([d['ricoverati_con_sintomi'] for d in data], dtype=np.int32)
    icus = np.array([d['terapia_intensiva'] for d in data], dtype=np.int32)
    isolated = np.array([d['isolamento_domiciliare'] for d in data], dtype=np.int32)
    currently_infected = np.array([d['totale_attualmente_positivi'] for d in data], dtype=np.int32)
    tested = np.array([d['tamponi'] for d in data], dtype=np.int32)

    infected = np.array(infected_list, dtype=np.int32)
    new_infected = infected[-1] - infected[-2]
    growth_rate = (infected[1:] - infected[:-1]) / infected[:-1]
    avg_growth_rate = moving_average(growth_rate, 5)

    # static forecast
    infected_forecast = infected_list.copy()
    infected_forecast_optimistic = infected_list.copy()
    infected_forecast_pessimistic = infected_list.copy()
    dates_forecast = dates.copy()

    for _ in range(10):
        infected_forecast.append(infected_forecast[-1] * (1 + growth_rate[-1]))
        infected_forecast_optimistic.append(
            infected_forecast_optimistic[-1] * (1 + growth_rate[-1] - 0.05))
        infected_forecast_pessimistic.append(
            infected_forecast_pessimistic[-1] * (1 + growth_rate[-1] + 0.05))

        dates_forecast.append(dates_forecast[-1] + timedelta(days=1))

    # dynamic forecast
    infected_dyn_forecast = infected_list.copy()
    infected_dyn_forecast_optimistic = infected_list.copy()
    infected_dyn_forecast_super_optimistic = infected_list.copy()
    dates_dyn_forecast = dates.copy()

    for i in range(10):
        infected_dyn_forecast.append(
            infected_dyn_forecast[-1] * (1 + growth_rate[-1] - growth_rate[-1] / 30 * i))
        infected_dyn_forecast_optimistic.append(
            infected_dyn_forecast_optimistic[-1] * (1 + growth_rate[-1] - growth_rate[-1] / 20 * i))
        infected_dyn_forecast_super_optimistic.append(
            infected_dyn_forecast_super_optimistic[-1] * (
                    1 + growth_rate[-1] - growth_rate[-1] / 10 * i))

        dates_dyn_forecast.append(dates_dyn_forecast[-1] + timedelta(days=1))

    with open(pathlib.Path() / 'report' / 'report.md', 'w') as f:
        f.write("<div align='center'>\n\n")
        f.write(f"# {str(dates[-1])[:10]}\n")
        f.write("CoVid-19 Italy Monitoring\n")
        f.write("</div>\n")
        f.write("\n")
        f.write(f"##### Total number of infected individuals is {infected[-1]}\n")
        f.write(f"##### Total number of recovered individuals is {recovered[-1]}\n")
        f.write(f"##### Total number of dead individuals is {dead[-1]}\n")
        f.write(f"##### Total number of tested individuals is {tested[-1]}\n")
        f.write("\n")
        f.write(f"##### Current number of infected individuals is {currently_infected[-1]}\n")
        f.write(f"- *hospitalized individuals* are {hospitalized[-1]}\n")
        f.write(f"- *hospitalized individuals are ICU* is {icus[-1]}\n")
        f.write(f"- home isolated individuals are {isolated[-1]}\n")
        f.write("\n")
        f.write(f"##### Number of new infected is {new_infected}\n")
        f.write("\n")
        f.write(f"##### Growth rate is {growth_rate[-1]:.2f} (5 days smoothing is"
                f" {avg_growth_rate[-1]:.2f})\n")
        f.write("![stats][stats]\n")
        f.write(f"##### Static forecast with the current growth rate ({growth_rate[-1]:.2f})\n")
        f.write(f"- after 3 days: {int(infected[-1] * math.pow(1 + growth_rate[-1], 3))}\n")
        f.write(f"- after 5 days: {int(infected[-1] * math.pow(1 + growth_rate[-1], 5))}\n")
        f.write(f"- after 10 days: {int(infected[-1] * math.pow(1 + growth_rate[-1], 10))}\n")
        f.write(f"##### Static forecast (growth rate = {growth_rate[-1] - 0.05:.2f})\n")
        f.write(f"- after 3 days: {int(infected[-1] * math.pow(1 + growth_rate[-1] - 0.05, 3))}\n")
        f.write(f"- after 5 days: {int(infected[-1] * math.pow(1 + growth_rate[-1] - 0.05, 5))}\n")
        f.write(
            f"- after 10 days: {int(infected[-1] * math.pow(1 + growth_rate[-1] - 0.05, 10))}\n")
        f.write(f"##### Static forecast (growth rate = {growth_rate[-1] + 0.05:.2f})\n")
        f.write(f"- after 3 days: {int(infected[-1] * math.pow(1 + growth_rate[-1] + 0.05, 3))}\n")
        f.write(f"- after 5 days: {int(infected[-1] * math.pow(1 + growth_rate[-1] + 0.05, 5))}\n")
        f.write(
            f"- after 10 days: {int(infected[-1] * math.pow(1 + growth_rate[-1] + 0.05, 10))}\n")
        f.write("![static_forecast][static_forecast]\n")
        f.write("\n")
        f.write(f"##### Dynamic forecast with a decreasing growth rate\n")
        f.write(f"- after 3 days: {int(infected_dyn_forecast[-8])}\n")
        f.write(f"- after 5 days: {int(infected_dyn_forecast[-6])}\n")
        f.write(f"- after 10 days: {int(infected_dyn_forecast[-1])}\n")
        f.write(f"##### Dynamic forecast with a fast decreasing growth rate\n")
        f.write(f"- after 3 days: {int(infected_dyn_forecast_optimistic[-8])}\n")
        f.write(f"- after 5 days: {int(infected_dyn_forecast_optimistic[-6])}\n")
        f.write(f"- after 10 days: {int(infected_dyn_forecast_optimistic[-1])}\n")
        f.write(f"##### Dynamic forecast with a super fast decreasing growth rate\n")
        f.write(f"- after 3 days: {int(infected_dyn_forecast_super_optimistic[-8])}\n")
        f.write(f"- after 5 days: {int(infected_dyn_forecast_super_optimistic[-6])}\n")
        f.write(f"- after 10 days: {int(infected_dyn_forecast_super_optimistic[-1])}\n")
        f.write("\n")
        f.write("![dynamic_forecast][dynamic_forecast]\n")
        f.write("\n")
        f.write("[stats]: stats.png\n")
        f.write("[static_forecast]: static_forecast.png\n")
        f.write("[dynamic_forecast]: dynamic_forecast.png\n")

    plt.rc('lines', linewidth=3, markersize=8)
    plt.rc('font', size=12)

    with plt.xkcd():
        fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(nrows=2, ncols=3, figsize=(15, 15))

        ax1.plot(dates, infected, 'o-', label='total infected')
        ax1.plot(dates, recovered, 'o-', label='total recovered')
        ax1.plot(dates, dead, 'o-', label='total dead')
        ax1.legend(loc='upper left')

        fig.autofmt_xdate()

        ax2.plot(dates, infected, 'o-', label='total infected\nin log scale')
        ax2.set_yscale('log')
        ax2.legend(loc='upper left')

        ax3.plot(dates, currently_infected, 'o-', label='currently infected')
        ax3.legend(loc='upper left')

        ax4.plot(dates[1:], growth_rate, 'o-', label='growth rate')
        ax4.plot(dates[5:], avg_growth_rate, label='5 days smoothing')
        ax4.legend(loc='upper right')

        ax5.plot(dates, hospitalized, 'o-', label='hospitalized')
        ax5.plot(dates, icus, 'o-', label='hospitalized (in ICU)')
        ax5.plot(dates, isolated, 'o-', label='home isolation')
        ax5.legend(loc='upper left')

        ax6.plot(dates, tested, 'o-', label='total tested')
        ax6.legend(loc='upper left')

        plt.savefig('report/stats.png')

    with plt.xkcd():
        fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(15, 15))

        fig.autofmt_xdate()

        ax1.plot(dates_forecast, infected_forecast, '*-', label='forecast')
        ax1.plot(dates, infected, 'o-', label='actual')

        ax1.set_title(f'infected in the next 10 days\nw/ the current growth rate'
                      f' {growth_rate[-1]:.2f}')
        ax1.legend(loc='upper left')

        ax2.plot(dates_forecast, infected_forecast_optimistic, '*-', label='forecast')
        ax2.plot(dates, infected, 'o-', label='actual')
        ax2.set_title(f'infected in the next 10 days\nw/ growth rate'
                      f' {growth_rate[-1] - 0.05:.2f}\n('
                      f'optimistic)')
        ax2.legend(loc='upper left')

        ax3.plot(dates_forecast, infected_forecast_pessimistic, '*-', label='forecast')
        ax3.plot(dates, infected, 'o-', label='actual')
        ax3.set_title(f'infected in the next 10 days\nw/ growth rate'
                      f' {growth_rate[-1] + 0.05:.2f}\n('
                      f'pessimistic)')
        ax3.legend(loc='upper left')

        plt.savefig('report/static_forecast.png')

    with plt.xkcd():
        fig, (ax1, ax2, ax3) = plt.subplots(nrows=1, ncols=3, figsize=(15, 15))

        fig.autofmt_xdate()

        ax1.plot(dates_dyn_forecast, infected_dyn_forecast, '*-', label='forecast')
        ax1.plot(dates, infected, 'o-', label='actual')

        ax1.set_title(f'infected in the next 10 days\nw/ a decreasing growth rate')
        ax1.legend(loc='upper left')

        ax2.plot(dates_dyn_forecast, infected_dyn_forecast_optimistic, '*-', label='forecast')
        ax2.plot(dates, infected, 'o-', label='actual')
        ax2.set_title(f'infected in the next 10 days\nw/ a fast decreasing growth rate\n('
                      f'optimistic)')
        ax2.legend(loc='upper left')

        ax3.plot(dates_dyn_forecast, infected_dyn_forecast_super_optimistic, '*-', label='forecast')
        ax3.plot(dates, infected, 'o-', label='actual')
        ax3.set_title(f'infected in the next 10 days\nw/ a super fast decreasing growth rate\n('
                      f'super optimistic)')
        ax3.legend(loc='upper left')

        plt.savefig('report/dynamic_forecast.png')
