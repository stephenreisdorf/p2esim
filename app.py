import random
import numpy as np
import plotly.graph_objects as go

import streamlit as st

class Die:

    def __init__(self, faces):
        self.faces = faces

    def roll(self):
        return random.randint(1,self.faces)

class Roll:

    @staticmethod
    def parse_roll_string(roll_string):
        # Split on '+' after removing spaces
        roll_terms = [ x for x in roll_string.replace(' ', '').split('+') ]
        dice_terms = [ x for x in roll_terms if 'd' in x ]
        modifier_terms = [ int(x) for x in roll_terms if 'd' not in x ]
        modifier = sum(modifier_terms)
        dice = []
        for d in dice_terms:
            num, faces = d.split('d')
            num = 1 if num == '' else int(num)
            faces = int(faces)
            for i in range(1,int(num)+1):
                dice.append(Die(faces))
        return Roll(dice, modifier)

    def __init__(self, dice, modifier):
        self.dice = dice
        self.modifier = modifier

    def roll(self):
        return sum([ d.roll() for d in self.dice ]) + self.modifier

class Target:

    def __init__(self, ac, fortitude, reflex, will):
        self.ac = ac
        self.fortitude = fortitude
        self.reflex = reflex
        self.will = will

class Attack:

    def __init__(self, damage, modifier, target):
        self.damage = damage
        self.modifier = modifier
        self.target = target

    def simulate(self):
        roll = random.randint(1,20) + self.modifier
        dc = self.target.ac
        if roll >= dc + 10:
            result = 'Critical Hit'
            damage = self.damage.roll() * 2
        elif roll >= dc:
            result = 'Hit'
            damage = self.damage.roll()
        elif roll >= dc - 10:
            result = 'Miss'
            damage = 0
        else:
            result = 'Critical Miss'
            damage = 0
        return roll, result, damage

    def sample(self, n=1000):
        full_sample = [ self.simulate() for i in range(0,n) ]
        rolls = np.array([ x for x,_,_ in full_sample ])
        results = np.array([ x for _,x,_ in full_sample ])
        damage = np.array([ x for _,_,x in full_sample ])
        return rolls, results, damage

st.set_page_config(layout='wide')
st.title('Pathfinder Simulator')

attack = Attack(
    damage=Roll.parse_roll_string(st.sidebar.text_input('Damage Roll', value='d8+4'))
    , modifier=st.sidebar.slider('Attack Modifier', value=7, min_value=1, max_value=50)
    , target=Target(
        ac = st.sidebar.slider('Target AC', value=15, min_value=1, max_value=50)
        , fortitude = 0 #st.sidebar.slider('Target Fortitude Save', value=15, min_value=1, max_value=50)
        , reflex = 0 #st.sidebar.slider('Target Reflex Save', value=15, min_value=1, max_value=50)
        , will = 0 #st.sidebar.slider('Target Will Save', value=15, min_value=1, max_value=50)
    )
)

run_simulation = st.sidebar.button('Simulate')
col1, col2 = st.beta_columns(2)

if run_simulation:
    rolls, results, damages = attack.sample()
    with col1:
        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x=damages
                , histnorm='probability'
            )
        )
        fig.update_layout(
            yaxis={ 'tickformat': '.0%'}
        )
        st.header('Damage Distribution')
        st.plotly_chart(fig)

        fig2 = go.Figure()
        fig2.add_trace(
            go.Histogram(
                x=damages
                , histnorm='probability'
                , cumulative_enabled=True
            )
        )
        fig2.update_layout(
            yaxis={ 'tickformat': '.0%'}
        )
        st.header('Cumulative Damage Distribution')
        st.plotly_chart(fig2)
    
    with col2:
        crit_chance = sum(results == 'Critical Hit') / len(results)
        hit_chance = sum(results == 'Hit') / len(results) + crit_chance 
        st.text('Hit chance {:.1%}'.format(hit_chance))
        st.text('Crit chance {:.1%}'.format(crit_chance))
        st.text('Expected damage: {:.2f}'.format(np.mean(damages)))
        st.text('Damage variance: {:.2f}'.format(np.std(damages)))