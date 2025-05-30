Estimate load:

   For Loadtest.js, these were:

    { duration: '30s', target: 10 }, // Ramp-up to 10 VUs in 30s
    { duration: '30s', target: 15 }, // Hold at 15 VUs for 30s
    { duration: '30s', target: 50 }, // Ramp-up to 50 VUs over 30s
    { duration: '30s', target: 75 }, // Ramp-up to 75 VUs over 30s
    { duration: '30s', target: 100 }, // Ramp-up to 100 VUs over 30s
    { duration: '1m', target: 100 }, // Hold at 100 VUs for 1 minute
    { duration: '30s', target: 50 }, // Ramp-down to 50 VUs in 30 seconds
    { duration: '30s', target: 10 },  // Ramp-down to 10 VUs in 30s
    { duration: '1m', target: 0 },  // Ramp-down to 0 VUs in 1 minute (graceful stop)


The total results were :
- 69% had a response time of <5s

Based on the req_duration:
- the average is just above the target : avg=5.79s
- the median shows that the virtuals users from approximatly 1-30 were pretty fast :med=1.71s 

But since p(90)=17.62s, from approximatly 40 to 50 the response starts to aggravate.
Finally, p(95)=29.53s, so around 60 the system is too overloaded !!

In conclusion, using k6 we found that we can scale up to 30 VU with our current infrastrucutre.


      