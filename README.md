# CS512

The test data is the first 10,000 lines of the January file for Chicago.

# Notes
09/04 - The code relies on generator functions to keep the memory pressure very low.
        The code relies on the nltk package and the emoji package. If they are not
        installed the code will attempt to install them using pip. At the conclusion
        of the current generator chain yields a dictionary for each tweet separating
        the 'words','hashtags',and 'emojis'. We should be able to do some analytics 
        with this. Also License is MIT and this README was added.
