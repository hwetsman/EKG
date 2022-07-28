This script was inspired by [watchlib](https://github.com/marcjulianschwarz/watchlib) and Apple's lack of identification of Premature Atrial Contractions (PACs) in the watch app. PACs may be a precursor to Atrial Fib (AF) or not. But I thought it was a good idea have the ability to examine the data.

## Installation
To use this script, just place it in the directory in which your apple watch zip file was unzipped. So you should see both this script and apple_health_export directory in the same directory.


## Functions: 
The script is enabled is run in streamlit and requires that to function. 
`pip install streamlit` will get that for you. 
The script contains 3 functions in the sideboard to chose from. The first is to create a dataframe of the EKGs in your watch data. Next, there is the ability to visualize an EKG of your choosing with filters for year and month. Lastly there is the ability to see PACs in the dataset across time.

## License: 
You may use this without limit for any personal use. Attribution would be appreciated. If you envision any commercialization, even free inclusion on an application that even indirectly supports a for-profit business, I would like to have a talk with you first.
