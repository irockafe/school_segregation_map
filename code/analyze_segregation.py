# TODO: compare nearby schools to racial and class composition
# TODO - calculate the racial breakdowns outside of the School() class, they should be much faster
#        than going elementwise
class School:
    def __init__(self, school_id:int, data, kd_tree):
        # NCESSCHID number
        # load up the dataframe containing all that info
        self.data = data
        self.school_id = school_id
        self.kd_tree = kd_tree  # in meters
        self.races = ['AM', 'AS', 'HI', 'BL', 'WH', 'HP', 'TR']
        number_grades = ['0%s' % i for i in range(1,10)] + ['%s' % i for i in range(10,14)]
        self.grades = ['PK', 'KG'] + number_grades
        self.race_columns = (['%s%s%s' % (race, grade, gender) for race in self.races
                                 for grade in self.grades
                                    for gender in ['M', 'F']]
                             )
        '''
        ['PKM', 'PKF', 'KGM', 'KGF'] +
                              ['0%s%s' % (i, j) for i in range(1,10) for j in ['M', 'F']] +
                              ['%s%s' % (i, j) for i in range(10,14) for j in ['M', 'F']]
                             )
        '''
    def grades_served(self):
        ''' 
        returns the grades with more than 0 students
        
        '''
        col_names = ['KG'] + ['G0%s' % i for i in range(1,10)] + ['G%s' % i for i in range(10,14)]
        grade_size = self.data.loc[self.school_id, col_names]
        grades = grade_size[grade_size > 0].index
        return grades


    def raw_race_data(self):
        '''
        Returns the entries containing racial info from dataframe.
        # AM american indian
        # AS asian
        # HI hispanic
        # BLK black
        # WH white
        # HP Hawaiian native/pacific islander
        # TR Two or more races
        '''
        # Note, ignoring adult edu and ungraded students here.
        #grade_levels = self.grades_served()
        # TODO replace this with a regex that searches for the grades
        students = self.data.loc[self.school_id, self.race_columns]
        # replace negative number with zeros
        students[students < 0] = 0
        return students
    
    
    def racial_breakdown(self, raw_race_data):
        '''
        returns two Series, 
          - racial_breakdown actual number of students by race
        # AM american indian
        # AS asian
        # HI hispanic
        # BLK black
        # WH white
        # HP Hawaiian native/pacific islander
        # TR Two or more races
        '''# Note, ignoring adult edu and ungraded students here.
        races = ['AM', 'AS', 'HI', 'BL', 'WH', 'HP', 'TR']
        racial_breakdown = pd.Series(index=races)
        # raw_race_data = self.raw_race_data()
        for race in races:
            #one_race_population = student_races[student_races.index.str.contains(race)]
            one_race_population = raw_race_data[raw_race_data.index.str.contains(race)]
            racial_breakdown[race] = one_race_population.sum()
        return racial_breakdown
        

    def nearby_schools(self, radius):
        # grab all nearby schools within given radius
        # I pre-calculated some radii to speed up, but
        # maybe not necessary, so ignoring for now.
        # add it in with an if-statement if slow

        # radius is in miles b/c america, etc. Sorry, world!
        # get the xyz coords of our school
        school_grades = self.grades_served()
        school_idx = self.data.index.get_loc(self.school_id)
        mile2meter = 1609.34
        xyz_coord = (self.data
                            .loc[self.school_id, ['x', 'y', 'z']]
                            .values
                     )
        neighbor_indices = self.kd_tree.query_ball_point(xyz_coord, 
                                                  radius*mile2meter)
        # check if neighbors share the grades
        # make sure not to compare to self
        # we want to compare only to schools containing at least
        # one of the same grade.
        neighbor_ids_with_same_grades = []
        for neighbor_idx in neighbor_indices:
            neighbor_id = self.data.iloc[neighbor_idx,:].name
            shares_grades = self.neighbor_shares_grades(neighbor_id)
            if shares_grades:
                neighbor_ids_with_same_grades.append(neighbor_id)
            '''
            if neighbor_idx == school_idx:
                continue
            # get the NCESSHID from the index number
            grades_shared = self.shared_grades(neighbor_id)
            if not grades_shared.empty:
                neighbor_ids_with_same_grades.append(neighbor_id)
            '''
        return neighbor_ids_with_same_grades
    
    
    def neighbor_shares_grades(self, neighbor_id):
        # Tells you if two Ncesshid numbers are neighbors that have at least one grade in common
        if neighbor_id == self.school_id:
            return False  # Skip over comparing self to self
        grades_shared = self.shared_grades(neighbor_id)
        if not grades_shared.empty:
            return True
    
    def shared_grades(self, neighbor_id):
        # Both are NCESSHID numbers
        school_grades = self.grades_served()
        neighbor_grades = School(neighbor_id, self.data, self.kd_tree).grades_served()
        # Get all grades that aren't present in both schools and drop them
        disunion = school_grades.symmetric_difference(neighbor_grades)
        grades_shared = school_grades.drop(disunion, errors='ignore')
        return grades_shared
    
    
    def raw_race_data_neighbor_same_grades(self, neighbor_id):
        # Get the raw data only for grades shared between two schools
        neighbor = School(neighbor_id, self.data, self.kd_tree)
        neighbor_raw_race_data = neighbor.raw_race_data()
        shared_grades = self.shared_grades(neighbor_id).str.replace('G', '')
        
        # get the indices
        # replace this with a regex search for self.race_columns
        index = ['%s%s%s' % (race, grade, gender) 
                 for race in self.races 
                 for grade in shared_grades 
                 for gender in ['M', 'F']]
        return neighbor_raw_race_data[index]

    
    def racial_breakdown_region(self, neighbor_ids):
        # Get population of each racial group
        # for all schools within certain radius
        # This breakdown only contains racial data for the grades present in
        # the current School() object
        racial_population = self.racial_breakdown(self.raw_race_data())
        #print(races.index)
        df = pd.DataFrame(columns=[self.school_id] + neighbor_ids, 
                          index=self.races )
        df[self.school_id] = racial_population
        for neighbor_id in neighbor_ids:
            # Take race data only from neighboring school's grades that match current
            # School() Object's grades (avoid comparing an elementary school to a 
            # elem + middle school)
            race_data_matching_grades = self.raw_race_data_neighbor_same_grades(neighbor_id)
            races_summed = self.racial_breakdown(race_data_matching_grades)
            df[neighbor_id] = races_summed
        return df
    
    
    def enrichment_scores(self, racial_breakdown_region):
        '''
        Returns a pandas Panel with pairwise enrichment scores (% minority school_a / % minority school_b,
        indexed - race x school_id x school_id 
        
        TODO - need to include the number of given race and school population for filtering
           later
        '''
        racial_percentages = racial_breakdown_region / racial_breakdown_region.sum(axis=0)
        enrichment_store = pd.DataFrame(index=racial_breakdown_region.index, 
                                        columns=racial_breakdown_region.columns,
                                       ).drop(self.school_id, axis='columns')
        for race in racial_percentages.index:
            # TODO use itertools to do a permutation, to avoid all the excess computations
            # iterate through pairwise combos of schools
            for neighboring_school in racial_breakdown_region.columns:
                if neighboring_school == self.school_id:
                    continue
                #print('current entry in enrichment_store', enrichment_store[race][neighboring_school])
                enrichment_store.loc[race, neighboring_school] = (
                    racial_percentages.loc[race, self.school_id] / 
                    racial_percentages.loc[race, neighboring_school]
                    )
                '''
                df.loc[race, self.school_id, neighboring_school] = (
                    racial_percentages.loc[race, self.school_id] / 
                    racial_percentages.loc[race, neighboring_school]
                    )
                '''
        return enrichment_store


    def measure_segregation(nearby_schools, metric, racial_groups):
        # make methods for entropy, gini-coef, dissimilarity index
        # TODO - ? how to define racial_group, and presets
        #    - does order matter? [[dominant group], [disempowered group]]
        #    - something like racial_groups = [['WH'], ['BL']]
        #    - white/asian vs all others = [['WH', 'AS'], [*]]
        #    - White vs blk and latino = [['WH'], ['BL', 'HI']]
        pass