Generate a new star catalog for ubercal-like things


Going healpix by healpix seems like a bad idea.

Let's try to figure out a good way using random_id--which is a real between 0-100

first, let's see how many stars there are in our mag range at gal lat > 30

SELECT count(ra) FROM lsst_sim.simdr2 WHERE rmag > 17 and rmag < 17.3 and (galb > 30 or galb < -30) 


SELECT ra,dec,umag,gmag,rmag,imag,zmag,ymag,ring256 FROM lsst_sim.simdr2 WHERE rmag > 17 and rmag < 17.3 
started at 4:38pm.  


----

Running SELECT count(ra) FROM lsst_sim.simdr2 WHERE rmag > 17 and rmag < 17.3  and  ring256=564654
gave me 7

So if one HEALpix has 7, if I do random_id < 50, that should give me 3 per healpix. 


SELECT ra,dec,umag,gmag,rmag,imag,zmag,ymag,ring256 
FROM 
lsst_sim.simdr2 
WHERE 
rmag > 17 AND rmag < 17.3 
AND
(galb > 30 OR galb < -30)
AND
random_id < 50

ok, that seemed to work well. Let's do another one!

