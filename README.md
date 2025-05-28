python: 3.6

package:
- numpy
- [dit](https://github.com/dit/dit?tab=readme-ov-file) for information computation
- progressbar2
- openpyxl
- h5py
- matplotlib
- ffmpeg


workflow:
Collect collective data: 
- Run "parallel_master_Vicsek_collective.py" to run "Vicsek_collective.py" to obtain the collective data. 
- To calculate those information-theoretic quantities, run "parallel_master_inf_collective.py" to run "information_quantities.py" to obtain these data.
- To obtain relevant order parameters, run "order_parameters.py"
- Run "collect_information.py" to store information-theoretic data into a xlsx file called "inf_collective_8.xlsx". _8 means the number of bins you select is 8.
- Run "collect_order_parameters.py" to store order parameter  data into a xlsx file called "order_parameters.xlsx".
Collect pairwise data:
- Run "parallel_master_Vicsek_pairwise.py" to run "Vicsek_pairwise.py" to obtain the pairwise data. 
- To calculate those information-theoretic quantities and influence data, run "parallel_master_inf_pairwise.py" to run "inf_quantities.py" to obtain these data.
- Run "collect_data.py" to store relevant information-theoretic quantities and influence quantities into a xlsx file called "inf_pairwise_8.xlsx". _8 means the number of bins you select is 8.

Generate Video:
run Vicsek_video.py
