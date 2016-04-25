# Tested with gnuplot 4.6 patchlevel 6

FN_IN = system("echo $FN_IN")
FN_OUT = system("echo $FN_OUT")

# TODO
#cost_hot = system("echo $cost_hot") + 0
#cost_mutants = system("echo $cost_mutants") + 0
#Y_MAX = system("echo $Y_MAX")
#Y_TICS_INTERVAL = system("echo $Y_TICS_INTERVAL")

set terminal pdfcairo enhanced size 2in, 1.5in
set lmargin at screen 0.215
set rmargin at screen 0.935
set tmargin at screen 0.97
set bmargin at screen 0.23

set output FN_OUT

set xlabel "Fill rate (%)" offset 0  , 0.3
set ylabel "Latency (ms)"  offset 1.5, 0

set border lc rgb "#808080"
set grid back #lc rgb "#808080"
#set xtics nomirror scale 0.5,0 tc rgb "black"
#set ytics nomirror scale 0.5,0 tc rgb "#808080" autofreq 0, Y_TICS_INTERVAL
set xtics nomirror scale 0.5,0
set ytics nomirror scale 0.5,0 autofreq 0,200

set xrange [0 : 100]
set yrange [0 : ]

plot \
FN_IN u 2:($11/1000) w p pt 7 ps 0.1 lc rgb "red" not

#
#set linetype 1 lc rgb "blue"
#set linetype 2 lc rgb "brown"
#set linetype 3 lc rgb "red"
#
#BOX_WIDTH=0.4
#
#set arrow from (1-BOX_WIDTH/2),cost_hot to (2-BOX_WIDTH/2),cost_hot nohead lt 0 lw 4
#set arrow from 1,cost_hot to 1,cost_mutants size screen 0.04,25
#set label (sprintf("-%.2f%%", 100.0 * (cost_hot - cost_mutants)/cost_hot)) at (1-BOX_WIDTH*0.2),(cost_hot+cost_mutants)/2 right
#
#set style fill solid 0.15 #noborder
#
### boxxyerrorbars parameters
###   x  y  xlow  xhigh  ylow  yhigh
##
##plot \
##FN_IN u                   0:(0):($0-BOX_WIDTH/2):($0+BOX_WIDTH/2):(0):2:xtic(1) w boxxyerrorbars lc rgb "red"  not, \
##FN_IN u ($3 == 0 ? 1/0 : 0):2  :($0-BOX_WIDTH/2):($0+BOX_WIDTH/2):2  :4         w boxxyerrorbars lc rgb "blue" not
