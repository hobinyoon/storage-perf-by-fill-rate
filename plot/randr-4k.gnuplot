# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

set terminal pdfcairo enhanced size 2in, 1.5in
set lmargin at screen 0.215
set rmargin at screen 0.935
set tmargin at screen 0.965
set bmargin at screen 0.23

set output FN_OUT

set xlabel "Fill rate (%)" offset 0  , 0.3
set ylabel "Latency (us)"  offset 1.5, 0

set border lc rgb "#808080"
set grid back

set xtics nomirror scale 0.5,0
set ytics nomirror scale 0.5,0 #autofreq 0,200

set xrange [0 : 100]
set yrange [0 : ]

plot \
FN_IN u 2:4 w p pt 7 ps 0.1 lc rgb "red"   not
