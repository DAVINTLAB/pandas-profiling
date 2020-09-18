# Data Profiling [![](https://img.shields.io/badge/python-3-blue.svg)](https://www.python.org/)

### **Disclaimer: we are still updating the documentation for this repository.**

Data profiling is a tool that helps data analysts in the process of data analysis and understanding. It summarizes a given dataset with an informative report.

Based on [Pandas Profiling](https://github.com/pandas-profiling/pandas-profiling) 1.4.1.

- [Installation](#installation)
- [Usage](#usage)
  - [Getting started](#getting-started)
  - [Report example](#report-example)
- [Dependencies](#dependencies)
- [Citation](#citation)
- [About the Authors](#about-the-authors)

## Installation

Data Profiling can be installed by running ```pip install https://github.com/DAVINTLAB/pandas-profiling/archive/master.zip```.

## Usage

Data Profiling will return its report in the form of a page written in HTML.

### Getting started

The use of Jupyter Notebook is recommended as it can make the experience more interactive. The first step is to import the necessary libraries.
```python
import pandas as pd
from pandas_profiling import ProfileReport
```
A [pandas](https://pandas.pydata.org/) dataframe will serve as the dataset that will be used to generate the report. In this example, we are using the Iris dataset.
```python
df = pd.read_csv("https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data", encoding='UTF-8')
```
In Jupyter Notebook, simply calling the report will display it.
```python
ProfileReport(df)
```
For more visualizations related specifically to categorical data (the Bi-Dimensional Chord Diagram and the Data Table), use:
```python
ProfileReport(df, extended_report=True)
```

### Report example

Here is a comparison between Pandas Profiling 1.4.1 (a) and Data Profiling (b).

![alt text][report]

[report]: https://imgur.com/VU9WCua.png

## Dependencies

[Python 3](https://www.python.org/) is required in order to run Data Profiling. Also, the following Python libraries are used:

| Library                                               | Version |
|-------------------------------------------------------|---------|
| [pandas](https://pandas.pydata.org/)                  | 0.23.4  |
| [numpy](https://numpy.org/)                           | 1.15.4  |
| [matplotlib](https://matplotlib.org/2.1.2/index.html) | 3.0.2   |
| [jinja](http://jinja.pocoo.org/docs/2.10/)            | 2.10.0  |

Internet access is necessary to load the JavaScript libraries. The following JavaScript libraries are used:

| Library                                      | Version |
|----------------------------------------------|---------|
| [d3](https://d3js.org/)                      | 5.9.7   |
| [jquery](https://jquery.com/)                | 3.4.1   |
| [bootstrap](https://getbootstrap.com/)       | 3.3.6   |

## Citation

Please refer to this tool by citing the works indicated below.

**For the tool in general:**

A. M. P. Milani, “Preprocessing proﬁling model for visual analytics”, Master’s thesis, School of Technology, PUCRS, Porto Alegre, 2019. [Online]. Available: http://tede2.pucrs.br/tede2/handle/tede/9007

**For the Bi-Dimensional Chord Diagram and the Data Table, specifically:**

L. Ciocari, “Uso de visualização de dados para auxiliar no pré-processamento de dados categóricos”, Undergraduate thesis, School of Technology, PUCRS, Porto Alegre, 2019.

## About the Authors

We are members of the Data Visualization and Interaction Lab (DaVInt) at PUCRS:
- Isabel H. Manssour -- Professor Coordinator of DaVInt -- 2017-current.
- Alessandra M. P. Milani -- Master Student in Computer Science -- 2017-2019.
- Lucas B. Ciocari -- Graduate Student in Computer Science -- 2019-current.
- Lucas A. Loges -- Undergraduate Student in Computer Science -- 2019-current.

More information can be found [here](https://www.inf.pucrs.br/davint/).
