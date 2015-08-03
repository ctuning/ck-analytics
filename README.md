CK extensions - predictive analytics
====================================

This is a relatively stable repository used to simplify and unify
experimentation and expose it to predictive analytics
(statistical analysis, feature selection, machine learning).

Dependencies
============

Python:
* matplotlib
* scipy
* numpy
* sklearn-kit

On Ubuntu, you can install packages using:
> sudo apt-get install python-numpy python-scipy python-matplotlib python-pandas

Useful:

* Graphviz
* R (for statistical analysis and machine learning, though Python may be enough)

Authors
=======

* Grigori Fursin, cTuning foundation (France) / dividiti (UK)

License
=======
* BSD, 3-clause

Installation
============

> ck pull repo:ck-analytics

Modules with actions
======================

experiment - universal experiment entries

  * add - process and add experiment
  * convert_table_to_csv - Convert experiment table to CSV
  * delete_points - delete multiple points from multiple entries
  * filter - filter / pre-process data
  * get - get points from multiple entries
  * get_all_meta - get all meta information from all entries
  * html_viewer - view experiment as html
  * list_points - list all points in a given entry
  * load_point - load all info about a given point (and subpoint)
  * multi_stat_analysis - perform statistical analysis (with multiple points at the same time)
  * replay - replay experiment == the same as reproduce
  * reproduce - reproduce/replay/rerun a given experiment
  * rerun - rerun experiment == the same as reproduce
  * sort_table - sort table, substitute index with a sequence (html)
  * stat_analysis - process multiple experimental results and perform statistial analysis (including expected values)
  * substitute_x_with_loop - substitute x axis in table with a sequence

experiment.view - customizable views for experiments

graph - universal graphs for experiments

  * continuous_plot - update plot periodically (useful to demonstrate continuous experiments and active learning)
  * html_viewer - view graph in html
  * plot - plot graph
  * replay - replay saved graph (to always keep default graphs for interactive papers)

graph.dot - .dot graphs (graphviz - useful ot customize decision trees from predictive analytics)

  * convert_to_decision_tree - convert .dot file a universal decision tree (useful before converting into C code for adaptive applications and libraries)

math.frontier - detecting (Pareto) frontier for multi-objective optimizations

  * filter - filter experiments with multiple characteristics (performance, energy, accuracy, size, etc) to leave only points on a (Pareto) frontier

math.variation - analyzing variation of experimental results (min,max,average,expected values,etc)

  * analyze - analyze variation of experimental results including multiple expected values

model - universal predictive modeling

  * build - build predictive model
  * convert_to_csv - convert table to CSV
  * use - use existing model to predict values
  * validate - validate predictive model (detect mispredictions, calculate RMSE, etc)

model.r - predictive modeling via R

  * build - build predictive model
  * validate - validate predictive model

model.sklearn - predictive modeling via python-based scikit-learn

  * build - build predictive model
  * convert_categories_to_floats - convert categories to floats
  * validate - validate predictive model

report - preparing experimental reports (html)

  * html_viewer - view report as html

table - preparing experimental tables (txt,html)

  * draw - draw experiment table (in txt or html)
