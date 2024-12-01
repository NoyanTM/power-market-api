# power-market-api

## Installation
- Download python3.x (3.10+)
- Create virtual environment: `python3 -m venv venv`
- Activate virtual environment: `source venv/bin/activate`
- Install packages: `pip install -r requirements.txt`
- Start API with: `uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload`

## TODO:
- отложенные задачи с background tasks на POST и корректный вывод ошибок из них (если упадет exception во время его выполнения, то при получении статуса задачи через GET нужно узнать причину и состояние чтоб пользовать нормально понимал)
- upload_data
  - доделать функциональность загрузки данных через file_body
    - possible to upload both file and body? или разделить это на 2 роута отдельный - upload_file / upload_data
  - добавить examples что необходимо передать в body или отображение description pydantic модели в custom swagger
  - попробовать сделать валидацию по содержанию файла
    - однако это необходимо сделать оптимизированно ведь крупные файлы так затруднительно валидировать
      - может вообще валидацию не стоит сделать? то тогда analysis и prediction выпадет с ошибкой если файл неверно сформированный. может тогда стоит доп. pipeline трансформации предусмотреть?
      - может стоит сделать это в виде отложенной задачи?
      - может не стоит валидировать весь файл, а лишь до первой ошибки и после этого выдавать exception?
    - python-magic file validation of magic bytes.
    - заключить все правила обработки загрузки файла через кастомный "file middleware": туда и ограничения по размеру, batched загрузку и валидацию вставить.
  - вместо хранения в файловой системе можно попробовать сделать интерфейс через s3 / database blob / оперативная память на время как temporary file.
  - optional upload multiple file / list of file body
- get_analysis:
  - matrix_json_str or other json_data - поменять формат x, y, z должно быть а не flat list dict
  - data aggregation / resample
  - individual legends and colorbar for every subplot
  - сократить количество копирования dataframe и разбить на разные функции функционал
  - сохранение анализа как файл и в базе
  - фильтрация для анализа по данным внутри query params - filter_params: Annotated[AnalysisFilterParams, Query()]
    - filter by obj_name, start_date, end_date, etc.
    ```
    weather_pivot = df_weather_temperature[(df_weather_temperature['object_name'] == 'Zadarya') & (df_weather_temperature['year'] == 2023)].pivot(index='hour', columns='day_of_year', values='temperature')
    df_filtered = df[(df.index >= start_date) & (df.index <= end_date) & (df['object_name'] == obj_name)]
    df_filtered = df_filtered[(df_filtered['plan'].notna() & df_filtered['plan'] != 0) | (df_filtered['fact'].notna() & df_filtered['fact'] != 0)]
    zadarya_2023 = df[(df['object_name'] == 'Zadarya') & (df['year'] == 2023) & (df['month'] != 12)] (df['month'] != 12)
    df_filtered = df[(df.index >= start_date) & (df.index <= end_date) & (df['object_name'] == 'Zadarya')]
    ```
    - check if the filtered dataFrame is empty, if not so raise exception like "No data available for the selected period and filters: {filters_list}"
- schemas:
  - create pydantic aliases for column titles.
  - отредачить формат некоторых полей, ведь в csv некоторые данные передаются в ковычках вместо numeric like "0,144".
  - валидация дат по другому формату и валидация логики start_date < end_date (тут мб пропускать если всего лишь одна запись есть), также надо брать из исходного файла минимальную и максимальную дату а не только ту что укажет пользователь
  - еще нам нужно порог по записям а то train и test не смогут работать - то есть минимально должно быть сколько то N записи и расстояние по времени 24 часа (start и end)
