
## INSTRUCTIONS
###############

# NOTE: tested on python 3.7

# unzip the bnp_test.zip archive
# This will create trade_acceptance folder (the distribution), with another trade_acceptance folder inside (the actual library)

# cd into top level trade_acceptance folder

# create and activate virtualenv

# install requirements
pip install -r requirements.txt

# install trade_acceptance package
pip install .

# run tests
pytest tests

# run script with sample input
# NOTE: changed script name to bnp_test.py, as bnp-test is not importable
cd trade_acceptance
python bnp_test.py input.xml

# output will appear in local folder as results.csv

# run benchmarks
cd ../tests
python benchmarks.py


# NOTES
#######

# performance / complexity
* A set of larger sample input files (generated with script trade_acceptance/generate_random_input) is provided
  (in the tests/data folder). This is used by tests/benchmark.py to test time and memory complexity of the script
* Due to the nature of the task, we can expect to have to iterate over the input records once,
  so complexity will be at least linear (O(n)) on the number of records.
  Sorting the output requires iterating over the number of CorrelationID's, which will impact performance.
  This is roughly confirmed by the output of tests/benchmark.py (although it seems to get worse from 1M to 10M records)
* In terms of memory usage, the use of iterators minimizes this, and we should expect a roughly constant usage.
  However the need to keep track of multi-record groups will cause a certain increase in memory usage,
  depending on percentage of multi-record groups
  Again the need to sort the ouput also has an impact, as we need to store the whole set of groups at the end prior to sorting
  This is also roughly observed when running tests/benchmark.py, although for > 10K records it seems that memory usage is impacted more

# Issues / Todo

* Output is sorted by CorrelationID *numerically*, which seems the most reasonable given the fact that ids
  seem to be integers in sample (despite the fact that the are spec'ed as strings)

* No validation is performed on input, so malformed entries can lead to wrong / misleading results
  For example, if a group contains more trades than specified in the field "NumberOfTrades",
  this will create a second entry for the same CorrelationID in the output.
  Dealing with this particular case would require to keep track of previously accepted trades,
  which would impact memory usage, and so it's not done as  it is not explicitly required