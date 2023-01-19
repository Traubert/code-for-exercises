---
topic: installing
title: Exercise - Fetch text data in VRT format and do topic modeling on it
---

<!-- | 💬    | General instructions or description | -->
<!-- | 💭    | Provide extra information or insight | -->
<!-- | 💡    | Valuable information, ideas or suggestions | -->
<!-- | ☝🏻    | Notice or a side-note | -->
<!-- | ‼️ Important information    -->

# Exercise - Fetch text data in VRT format and do topic modeling on it

💬 In this exercise we will experiment with a common task for text, topic modeling. You can go through the tutorial step by step and do all the exercises, run a script that does the steps for you, or just read it. The exercises are in the form of Python code that you can edit to make it run faster. Solutions are included.

## Data


💬 The Language Bank of Finland keeps its analyzed text data in a format called [https://www.kielipankki.fi/development/korp/corpus-input-format/](VRT). VRT is used because it's the format of the [IMG Open Corpus Workbench](http://cwb.sourceforge.net/) (CWB), so it's not exactly a common standard, but it's easy enough to use for many purposes. We will fetch some VRT files, extract the lemmas, and use the lemmas as input to a topic modeling package.

The Language Bank maintains a [https://www.kielipankki.fi/corpora/](directory of corpora) which you can browse for corpora available to you. Each corpus is listed with license information: PUB means available to everyone, ACA means available for users affiliated with an academic institution, RES means you have to apply for access.

☝🏻 First, hop into an interacive computing node with `sinteractive --time 08:00:00 --mem 32000 --cores 4`, it will prompt you to select a CSC project. `--time 08:00:00` means that the node will kick you out after 8 hours. If you exit the node before then, you will save on billing units; the reservation is more for scheduling than billing purposes. `--mem 6000` means 6000 megabytes, and `--cores 4` means you will be able to run that many processes simultaneously (for this small example).

You'll also need a directory in which to work, it's up to you, but making a directory for this under `scratch/project/<your_username>` is a good choice, since we're just trying things out. You can make sure that this directory exists with `mkdir -p /scratch/<project>/$USER`. In that directory, fetch some starter code into a new directory with `git clone https://github.com/Traubert/code-for-exercises.git csc-exercises` FIXME REPO. Then `cd csc-exercises/topics` into the directory for this exercise. This will be our workspace.

💡 If you are a member of the `kieli` group on `puhti`, you can find read-only VRT data under `/appl/data/kielipankki/`. Otherwise, you can follow download links from the corpus directory.

The rest of this example will use the YLE news in Finnish corpus, which can be downloaded [here](https://korp.csc.fi/download/YLE/fi/2011-2018-s-vrt/). The commnds that follow you can either type in by hand, or run the included script FIXME, which should do everything up to the end of this tutorial FIXME

```
$ wget https://korp.csc.fi/download/YLE/fi/2019-2021-s-vrt/ylenews-fi-2019-2021-s-vrt.zip

$ unzip ylenews-fi-2019-2021-s-vrt.zip
Archive:  ylenews-fi-2019-2021-s-vrt.zip
   creating: ylenews-fi-2019-2021-s-vrt/
   creating: ylenews-fi-2019-2021-s-vrt/vrt/
  inflating: ylenews-fi-2019-2021-s-vrt/vrt/ylenews_fi_2019_s.vrt
  inflating: ylenews-fi-2019-2021-s-vrt/vrt/ylenews_fi_2021_s.vrt
  inflating: ylenews-fi-2019-2021-s-vrt/vrt/ylenews_fi_2020_s.vrt
  inflating: ylenews-fi-2019-2021-s-vrt/README.txt
  inflating: ylenews-fi-2019-2021-s-vrt/LICENSE.txt
```

We should now have three VRT files under `ylenews-fi-2019-2021-s-vrt/vrt` of roughly two gigabytes each.

### Data format

💭 Let's take a quick look at the files so we have some idea of what we're dealing with:

```
$ head ylenews-fi-2019-2021-s-vrt/vrt/ylenews_fi_2019_s.vrt 
<!-- #vrt positional-attributes: word ref lemma lemmacomp pos msd dephead deprel lex/ -->
<!-- #vrt info: VRT generated from CWB data for corpus "ylenews_fi_2019_s" (2022-08-24 11:38:39 +0300) -->
<!-- #vrt info: A processing log at the end of file -->
<text datetime_content_modified="2018-12-31T23:46:26+0200" datetime_json_modified="2020-09-23T12:41:54+0300" datetime_published="2018-12-31T23:46:26+0200" datefrom="20181231" dateto="20181231" departments="|Näkökulmat|" id="20-280865" main_department="Näkökulmat" publisher="yle-aihe" timefrom="234626" timeto="234626" url="https://yle.fi/aihe/artikkeli/2018/12/31/matkakertomuksia-osa-vi-v-tilanne-verhon-edessa-osa-a">
<sentence id="1" type="text" paragraph_type="text">
Kun	1	kun	kun	C	SUBCAT_CS|CASECHANGE_Up	2	mark	|kun..kn.1|
käännyin	2	kääntyä	kääntyä	V	PRS_Sg1|VOICE_Act|TENSE_Prt|MOOD_Ind	5	advcl	|kääntyä..vb.1|
katsomaan	3	katsoa	katsoa	V	NUM_Sg|CASE_Ill|VOICE_Act|INF_Inf3	2	xcomp	|katsoa..vb.1|
,	4	,	,	Punct	_	2	punct	|,..xx.1|
huomasin	5	huomata	huomata	V	PRS_Sg1|VOICE_Act|TENSE_Prt|MOOD_Ind	0	ROOT	|huomata..vb.1|
```

VRT is a pseudo-xml format. By pseudo I mean that it doesn't have a root node, but is instead a sequence of `text` elements. (There are some other differences but that's not important right now.) The leaf nodes which contain text (here, `sentence`), have one token per line, with fields separated by tabs. So it's a TSV (tab-separated values) format inside an XML-like format. The first line indicates what the fields mean; the first one is `word`, for word form, the second is `ref`, for token number, `lemma` for lemma and so on.

💭 You may notice that the `text` element has some interesting attributes, like `departments`, `main_department` and `publisher`. Unfortunately the `main_department` is usually empty (the commands are `unix` tools available on every system):

```
$ grep --only-matching 'main_department="[^"]*' ylenews-fi-2019-2021-s-vrt/vrt/ylenews_fi_2019_s.vrt | cut -b18- | sort | uniq -c | sort -nr
  62104 
    319 Yle TV1
    263 Klassinen
    184 Yleisradio
    164 Luonto
    160 Strömsö
    160 Kulttuuricocktail
...
```

The `publisher` never is:

```
$ grep --only-matching 'publisher="[^"]*' ylenews-fi-2019-2021-s-vrt/vrt/ylenews_fi_2019_s.vrt | cut -b12- | sort | uniq -c | sort -nr
  38110 Yle Uutiset
  14104 Yle Urheilu
   8882 Yle Uutiset - lyhyet
   1301 yle-aihe
...
```

The attributes come from the data source, and there's no general rule as to what you can rely on. Clearly here `publisher` is somewhat meaningful and very reliable, `main_department` has more detail, but is very sparse (perhaps we could fill it in ourselves!).

## Dependencies

☝🏻 We are now going to install some dependencies. This can be done in many ways, some simpler than others, and some more efficient than others. You can skip to the commands at the end of section if you're not interested in the details.

There are essentially three alternatives for installing Python dependencies:

1) Installing them in your home directory with `pip install --user`. This quickly becomes unmaintainable with many projects and library versions.
2) Installing in a virtual environment with `venv` or `conda`. This has some downsides on the HPC systems, causing slow startup times and unnecessary IO load on the whole system.
3) An Apptainer container, for which we have our custom took `tykky`, which is usually the ideal option.

If you have a `requirements.txt` file, as we do here, installing them into a `tykky` environment is in principle simple, as long as your libraries support the default Python version, which at the time of writing is 3.6. Unfortunately, that's too old for us, so we'll first make a temporary `venv` in which to build the `tykky` container with python3.9. So we do:

```
$ mkdir tykky-env                                                                                 # the tykky environment will go here
$ python3.9 -m venv tmp-venv                                                                      # create a temporary venv with the correct Python version
$ source tmp-venv/bin/activate                                                                    # step into the venv
$ module load tykky                                                                               # load the tykky module
$ pip-containerize new --prefix /scratch/<project>/$USER/csc-exercises/topics requirements.txt    # or whatever directory you chose
$ deactivate                                                                                      # exit the temporary venv
rm -rf tmp-venv                                                                                   # not needed anymore
export PATH="/scratch/<project>/$USER/csc-training/topics/tykky-env/bin:$PATH"                    # make the tykky environment visible
```

For the rest of this session, your default Python environment will have the packages from `requirements.txt` installed. After logging out, things will be back to the way they were before. Then you can `export PATH` again, or set the path on every login in eg. `.bash_profile`.

💬 Moving on, we can try to run `parse_vrt.py`, which by default builds lists of lemmas of each text, and then does nothing with them. Let's time at as we go. It should look something like this:

```
$ python3 parse_vrt.py ylenews-fi-2019-2021-s-vrt/vrt
Running parse_vrt_in_dir...
  Reading ylenews-fi-2019-2021-s-vrt/vrt/ylenews_fi_2019_s.vrt
  Finished reading ylenews-fi-2019-2021-s-vrt/vrt/ylenews_fi_2019_s.vrt, 65811 texts and 25772447 tokens
  Reading ylenews-fi-2019-2021-s-vrt/vrt/ylenews_fi_2020_s.vrt
  Finished reading ylenews-fi-2019-2021-s-vrt/vrt/ylenews_fi_2020_s.vrt, 63004 texts and 27871609 tokens
  Reading ylenews-fi-2019-2021-s-vrt/vrt/ylenews_fi_2021_s.vrt
  Finished reading ylenews-fi-2019-2021-s-vrt/vrt/ylenews_fi_2021_s.vrt, 56543 texts and 25374938 tokens
...finished in 136.04 s
```

### First task

☝🏻 Your first task, should you choose to accept it, is to replace the sequential processing of VRT files in `parse_vrt.py` with parallel processing, and then verify that you are able to accomplish this step faster with parallel than sequential processing. One possible solution for this is included in `parse_vrt_solution.py`.

## Topic modelling

💬 Next we will use `gensim` to do some topic modeling. The Python script `topics.py` uses `parse_vrt.py` to get data, and processes it in various ways. Try running it with the same argument:

```
$ python3 topics.py ylenews-fi-2019-2021-s-vrt/vrt
Running parse_vrt_in_dir...
  Reading ylenews-fi-2019-2021-s-vrt/vrt/ylenews_fi_2019_s.vrt
  Finished reading ylenews-fi-2019-2021-s-vrt/vrt/ylenews_fi_2019_s.vrt, 65811 texts and 25772447 tokens
  Reading ylenews-fi-2019-2021-s-vrt/vrt/ylenews_fi_2020_s.vrt
  Finished reading ylenews-fi-2019-2021-s-vrt/vrt/ylenews_fi_2020_s.vrt, 63004 texts and 27871609 tokens
  Reading ylenews-fi-2019-2021-s-vrt/vrt/ylenews_fi_2021_s.vrt
  Finished reading ylenews-fi-2019-2021-s-vrt/vrt/ylenews_fi_2021_s.vrt, 56543 texts and 25374938 tokens
...finished in 133.77 s
Building gensim dictionary... Done in 21.49 s
Computing BOW corpus... Done in 14.11 s
Computing LDA model... Done in 114.99 s
[topic printout]
```

After the one step from the previous section, we have added three more sections. All of them can be parallelised, but not all of them offer the same potential. If you are interested in parallelising code, they are all interesting examples, but the most important practical skill is to recognise at this point that these steps represent 47%, 7%, 5% and 41% of the runtime respectively, so that is the ceiling to how much can be accomplished by speeding them up.

### Second task

### Bonus task 1
### Bonus task 2
