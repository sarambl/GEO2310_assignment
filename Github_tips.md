I've put together a few tips on git and github. You should really google git/github tutorial to learn more, but this might get you somewhat started. See also links [here](https://uio.instructure.com/courses/18345/pages/help-with-mandatory-assignment).

## Setup ssh connection to github:

1. As soon as you login at github.uio.no with your UiO user and password, you have a github account. 

2. [create new SSH keys](https://help.github.com/articles/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent/#generating-a-new-ssh-key).

3. Clone the GEO2310_public to your machine:
```bash
$ git clone git@github.uio.no:sarambl/GEO2310_public.git
```

## Make your own branch

```bash
$ git branch [branch-name]
```
Switch to branch to work on your new branch:
```bash
$ git checkout [branch-name]
```
Branch name should be something easy to understand. E.g. your user name or the names of the people collaborating.
## Make changes and commit them:

When you've swithced to your own branch, you can make as many changes as you want here, and you can still switch to the master branch later on (and everything will stay the same there). 
When you've made a change to some file and want to save a version of the document, you write

```bash
$ git add [file-name]
```
and then commit the change:
```bash
$ git commit -m 'Some message describing the current state of the project (what did you change etc)'
```

## Share your branch:
Write to me (Sara) and send me your user name and I can add you as a collaborator. Then you can push your new branch to the repository.
```bash
$ git push origin [branch-name]
```
## Get new changes:
If something is updated in the branch (e.g. by a collaborator), you may want those changes to be incorporated locally:
```bash
$ git pull
```
