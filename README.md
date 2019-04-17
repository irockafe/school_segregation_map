# school_segregation_map
## Goal
Enable universities and policy-makers to identify desegregatable schools -
schools that are significantly more white (also possibly east/south Asian, tbd**) than neighboring schools. 
This allows universities to incentivize integration by awarding bonus points to 
non-white enriched schools during admissions. 

Also, same idea, but for economic segregation using lunch data(? it might not be as useful as other data)

Credit for the idea to: 
  - [Tom Railton](https://ylpr.yale.edu/shifting-scope-how-taking-school-demographics-account-college-admissions-could-reduce-k-12)
  wrote the original idea up, as far as I know.
  - [lona Arnold-Berkovits](https://schoolbonuspoints.org/background-2.html) proposed some more robust studies
  - [Rachel Cohen](https://www.theatlantic.com/education/archive/2018/05/an-unusual-idea-for-fixing-school-segregation/560930/)
  Wrote up the idea for a broad audience at the Atlantic, where I initially read about it.

Usage
----------

**Install Docker and docker-compose**<br>
Follow instructions [here](https://docs.docker.com/install/)

**Build the container**<br>
`docker-compose build` 
<br>(this will take a while to download all the dependencies. Go grab tea.)

**Enter the container**<br>
`docker-compose run --rm project bash`
<br> Now you'll have a bash session within the container

## What's done so far?
- Convert DoE Civil Rights dataset of lon/lat school locations into 3d coordinates.
- Make a kd-tree from coordinates, get all neighbors within given distance of each schools
- Get difference in racial-composition/lunch-status between each school and its neighbors
   - Currently being simple, using percentage-point differences (i.e. School A is 80% white, school B is 30% white, 
   the point-difference is 50).

## To-do
- **Get better measure of distance** Currently distances don't account for roads, traffic, they're just straight lines. 
Fundraise or crowdsource using Gmaps distance-matrix API to get better measure - 15 miles in Iowa is a lot different 
from 15 miles in Boston.
    - **Speed up code** that set(pairwise-schools): {A: [B, C], B: [A], C: [A,B] } -> {A: [B,C], C:[B]} 
    I've got slow code (unique_school_pairs.py) that will eventually spit out a set of all neighbor-pairs.
    We'll feed those pairs into the distance-matrix API.
    - How to setup a server that gives crowd-sourcers an API call to run on their own free-tier instances?
    - How to make that as easy as possible? (and does it violate ToS?)
- **Find who's left behind by 1-dimensional measures of segregation** Look into race v. income measures and do parameter 
exploration of how many segregated students (econ or race) are left unincentivized when a single measurement is used
    - i.e. How many kids in racially-segregated schools get left unincentivized if I only use lunch data. Vice-versa?
    - I guess that ends up being a bunch of cumulative distribution functions for varying lunch/racial thresholds
- **Quantify how prevalent segregation is** Use a hypergeometric stat-test on each school vs. population of region
to quantify (pval) how surprised I am to find a school that segregated by random chance.
    - Currently (naively) thinking that the distribution of these pvals can tell us when integration on a state or national
    level has truly occured. There will always be some schools that are transiently segregated, but as long as the pval distribution
    of the state/nation as a whole is roughly uniform, we are actually integrated in a statistical sense.
- Write some tests, silly
