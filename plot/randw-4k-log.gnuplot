# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

set terminal pdfcairo enhanced size 2in, 1.5in
set lmargin at screen 0.215
set rmargin at screen 0.935
set tmargin at screen 0.97
set bmargin at screen 0.23

set output FN_OUT

set xlabel "Fill rate (%)" offset 0, 0.3
set ylabel "Latency (us)"  offset 0, 0

set border lc rgb "#808080"
set grid back
set xtics nomirror scale 0.5,0
set ytics nomirror scale 0.5,0 ( \
"10^4" 10000, \
"10^3"  1000, \
"10^2"   100, \
"10^1"    10 \
)

set xrange [0 : 100]
set yrange [10 : 10000]

set logscale y

plot \
FN_IN u 2:7 w p pt 7 ps 0.1 lc rgb "blue"  not, \
FN_IN u 2:9 w p pt 7 ps 0.1 lc rgb "brown" not, \
FN_IN u 2:8 w p pt 7 ps 0.1 lc rgb "red"   not
