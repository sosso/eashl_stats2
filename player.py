class Player():
    def __init__(self, values):
        try: self.member_name = values[17]
        except: self.member_name = ''
        try: self.goals = int(values[1])
        except: self.goals = -1
        try: self.assists = int(values[2])
        except: self.assists = -1
        try: self.pts = int(values[3])
        except: self.pts = -1
        try: self.plus_minus = int(values[4])
        except: self.plus_minus = -1
        try: self.pim = int(values[5])
        except: self.pim = -1
        try: self.ppg = int(values[6])
        except: self.ppg = -1
        try: self.shg = int(values[7])
        except: self.shg = -1
        try: self.hits = int(values[8])
        except: self.hits = -1
        try: self.blocked_shots = int(values[9])
        except: self.blocked_shots = -1
        try: self.shots = int(values[10])
        except: self.shots = -1
        try: self.shot_percentage = float(values[11])
        except: self.shot_percentage = -1
        try: self.gaa = float(values[12])
        except: self.gaa = -1
        try: self.goals_against = int(values[13])
        except: self.goals_against = -1
        try: self.saves = int(values[14])
        except: self.saves = -1
        try: self.save_percentage = float(values[15])
        except: self.save_percentage = -1
        try: self.shutouts = int(values[16])
        except: self.shutouts = -1

    def __unicode__(self):
        return "%s\t%s" % (self.member_name, self.online_status)
    def fields_in_row_format(self):
        return "%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%f\t%f\t%d\t%d\t%f\t%d" % (self.member_name, self.ranking, self.goals, self.assists, \
                                                                                       self.pts, self.plus_minus, self.pim, \
                                                                                        self.ppg, self.shg, self.hits, \
                                                                                        self.blocked_shots, self.shots, \
                                                                                        self.shot_percentage, self.gaa, \
                                                                                        self.goals_against, self.saves, \
                                                                                        self.save_percentage, self.shutouts)
    def fields_in_array_format(self):
        return [self.member_name, self.ranking, self.gp, self.goals, self.assists, \
                                                                                       self.pts, self.plus_minus, self.pim, \
                                                                                        self.ppg, self.shg, self.hits, \
                                                                                        self.blocked_shots, self.shots, \
                                                                                        self.shot_percentage, self.gaa, \
                                                                                        self.goals_against, self.saves, \
                                                                                        self.save_percentage, self.shutouts]

