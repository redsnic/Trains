%%% Input facts:
% cell/2
cell(0,0).
cell(0,1).
cell(0,2).
cell(0,3).
cell(0,4).
cell(0,5).
cell(0,6).
cell(0,7).
cell(0,8).
cell(0,9).
cell(1,0).
cell(1,1).
cell(1,2).
cell(1,3).
cell(1,4).
cell(1,5).
cell(1,6).
cell(1,7).
cell(1,8).
cell(1,9).
cell(2,0).
cell(2,1).
cell(2,2).
cell(2,3).
cell(2,4).
cell(2,5).
cell(2,6).
cell(2,7).
cell(2,8).
cell(2,9).
cell(3,0).
cell(3,1).
cell(3,2).
cell(3,3).
cell(3,4).
cell(3,5).
cell(3,6).
cell(3,7).
cell(3,8).
cell(3,9).
cell(4,0).
cell(4,1).
cell(4,2).
cell(4,3).
cell(4,4).
cell(4,5).
cell(4,6).
cell(4,7).
cell(4,8).
cell(4,9).
cell(5,0).
cell(5,1).
cell(5,2).
cell(5,3).
cell(5,4).
cell(5,5).
cell(5,6).
cell(5,7).
cell(5,8).
cell(5,9).
cell(6,0).
cell(6,1).
cell(6,2).
cell(6,3).
cell(6,4).
cell(6,5).
cell(6,6).
cell(6,7).
cell(6,8).
cell(6,9).
cell(7,0).
cell(7,1).
cell(7,2).
cell(7,3).
cell(7,4).
cell(7,5).
cell(7,6).
cell(7,7).
cell(7,8).
cell(7,9).
cell(8,0).
cell(8,1).
cell(8,2).
cell(8,3).
cell(8,4).
cell(8,5).
cell(8,6).
cell(8,7).
cell(8,8).
cell(8,9).
cell(9,0).
cell(9,1).
cell(9,2).
cell(9,3).
cell(9,4).
cell(9,5).
cell(9,6).
cell(9,7).
cell(9,8).
cell(9,9).
sum(X,Y,Z):- cell(X,Y), Z=X+Y.
#show sum/3.
