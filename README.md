# Lick analysis for WDIL experiment
Combine `mat` file with `excel` file to determine the lick rate during different phase of the behavior
`lickAnalysis.py`: script to extract lick information

## usage:
### instruction
*  install [Anaconda](https://www.anaconda.com/)
*  Start Anaconda command prompt
*  In the command prompt type: `python` then `space`
*  Drag and drop the file `lickAnalysis.py` then press `Enter`
*  Follow the instructions<!-- add `space` before drag and drop the **Folder** containing the files of interest -->
*  press `Enter`

## outputs:
This will generate the following:   
* `duplicates.csv`: a list of duplicates as some folder have duplicated session that needs to be currated prior to moving forward
* `licksAnalysisError.log`: a log file where some of the error are stored the script will run through everything just by passing error that can be tracked there
* `respTime.csv`: contains all the response times for licking
* `lickCount.csv`: contains all the lick count based on specific categorization see the [`State Matrix for Whisker Stimulation.docx`](State Matrix for Whisker Stimulation.docx)

## Notes
Detail about the state matrix is in the docx and all version of analyis are in the `deprecated` folder

[TODO improve readme]
