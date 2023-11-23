x = is(9);
y = is(6);
c1 = is(1);

test = {
    z = add(x,y);
    z = add(c1,z);
    return(z);
}

args = {x=add(x,y);}
k = test(args); // create a new scope, compute args in there, and run test to obtain its returned value
print(k);
print(x); // stays the same
