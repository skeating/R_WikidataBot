# ReactomeBot

This is a Wikidata bot that will take information from Reactome and create/update pages in Wikidata.

##Code

The bot is written in Python (requires v 3) and makes use of the [WikidataIntegrator](https://github.com/SuLab/WikidataIntegrator) developed by [the Su Lab](http://sulab.org/).

It is based on the [wikipathways\\_wikidata\\_bot](https://github.com/wikipathways/wikipathways_wikidata_bot) used for Wikidata entry written for [Wikipathways](http://www.wikipathways.org/index.php/WikiPathways).
 

### Usage

python ReactomeBot.py wikidata_username wikidata_password (inputfilename)

#### Input file

The code requires an comma separated value (.csv) file where each line refers to a Wikidata entry. The entries expected are:

**Species\_code,Reactome\_Id,Name,Description,[publication1;publication2;..],goterm,None**

where

- Species\_code is the three letter abbreviation of the species used by Reactome e.g. HSA
- Reactome\_Id is the Reactome Stable Indentifier for the pathway
- Name the Reactome Display Name
- Description a sentence based on Name stating that this is an instance of this pathway in the given species
- [publication1;..] a semi-colon separated list of the pmid URL of each referenced publication
- goterm teh relevant term as GO:nnnn
- None - to indicate the end of the entry
  
## TO DO



1. Once we have a Reactome ID property in Wikidata this needs to be added. 
2. Add support for identifying parent and child pathways that could be added to WSD as 'has part' and 'part of' properties.
3. Add support for adding reactome 'Reactions' that are not full pathways in the database.





