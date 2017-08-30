for letter in 'Python': 
   if letter == 'h':
      pass
      print 'Day la khoi pass'
   print 'Chu cai hien tai :', letter

print "Good bye!"

CREATE TABLE orgmyd08_d3
(
    sourceid integer DEFAULT 0, 
    aqstime timestamp without time zone,
    filename character(100),
    path character(100),
    id bigserial NOT NULL,
    updatetime timestamp without time zone,
    collection smallint,
    isdelete boolean DEFAULT false,
    CONSTRAINT orgmyd04_pkey PRIMARY KEY (id)
)
