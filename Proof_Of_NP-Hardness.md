# Proof of NP-Hardness
## the "train" problem is NP-hard

In this section we aim to show that the train problem is NP-hard and we do that by reducing the NP-complete **Hamiltonian circuit** problem to the train problem.

### Definitions:

Consider a generic Hamiltonian circuit instance. Let $G(V,E)$ be the undirected graph associoated to this instance and 
let $v \in E$ be the starting node. We create an instance of the train problem as follows:
1. We set $G(V,E)$ to be the graph describing all the possible routes of the trains, so $V$ is the set of stations and $E$ the set of the railroads.
* We set $v\in V$ to be the only station with a train deposit, with a maximum capacity of $1$, hence, the maximum nuber of trains is $1$.
* The weight of each edge is set to $1$
* We set $T=2|V|+3$ as the total number of time slots, so that is possible to move and stop at each station iff at any time it is possible to reach a never visited station (or to return to $v$) by traversing a single edge.   
* Even if not strictly necessary, we add the request of having a train from $v$ to $v$ and passing by $V\setminus \{v\}$

By point number 5, we have that the minimum ammount of time necessary to serve such a request is the sum of:
1. $1$ time slot for putting the train onto the rails at the beginnig of the operations
2. $V+1$ time slots for stopping in each station and two times in $v$
3. $V$ time slots for reaching the next stop 
4. $1$ time slot for putting the train in the parking of $v$

Having set, by point 4, the maximum nuber of time slots exactly to $2|V|+3$ this means that the solver might yeld a solution iff condition 5 is satisfied and there is not a the train does pass exactly one time by any station (as the ammount of time slots is not sufficient to permit repetitions of them). This means that the routes taken by the train exactly describe an Hamiltonian circuit.
We can finally conclude that this problem admits a solution iff there is an hamiltonian circuit in the graph $G=(V,E)$ and this proves the NP-hardness of this problem.

## Considerations on instance admissibility verification

Consider now a generic instance of a train problem:

1. the number of trains that are not still in a park is less than $|V|*T$ as any train must use a time slot to be prepared on a stop.
* the maximum nuber of times a train can reach a station is again bounded by $|V|*T$ for the same reasons as before
* the requests are at in a linear relation with the total length of the program. Let $R$ be the set of the requests  

points 1 and 2 combined states that the number occurring in the definition of the program are bounded by values polynomially related to the input. 

If we consider a generic solution to a generic instance of the train problem we can evaluate if it is admissible in
polynomial time (let $O$ be the output, by the previous consideration it has polynomial size and is structured as a timetable stating at each time where each train is):

1. we can check in polynomial time (in respect to $|O|$) whether two trains are in the same location (route or stop) at the same time or if there are too many trains stopping at a train station. 
2. we can check a direct reqest (eg. from A to B) easely looking for a train that stops at A at a certain time and then at B without any stop or park action in the middle, the way of reasoning is similar for the request with intermediate stops.
3. to test minimum number of connections request (eg. from A to B) we simply scan the timetables for each train and count the total nuber of times a train stops at A and then at B. 

Any other request is easly soved in polynomial time with similar strategies. We can then state that it is possible to evaluate admissibility in polinomyal time.





