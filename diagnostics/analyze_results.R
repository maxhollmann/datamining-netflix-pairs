p = function(...) cat(paste0(...), "\n")

files = Sys.glob("../res_*.csv")
nfiles = length(files)
tbl = data.frame()

if (nfiles == 0) stop("No files found")


par(mfrow = c(
  floor(sqrt(nfiles)) + (floor(sqrt(nfiles)) * ceiling(sqrt(nfiles)) < nfiles), 
  ceiling(sqrt(nfiles))
))

ds = lapply(files, function(file) {
  d = read.csv(file)
  colnames(d) = c("c1", "c2", "sig_sim", "jac_sim", "i", "time")
  d$count = seq_along(d$i)
  d
})
max_count = max(sapply(ds, function(d) max(d$count)))
min_time = min(sapply(ds, function(d) min(d$time)))
max_time = max(sapply(ds, function(d) max(d$time)))

for (i in 1:length(ds)) {
  d = ds[[i]]
  file = files[i]
  
  plot(count ~ time, d, xlim = c(min_time, max_time), ylim = c(0, max_count), main = file)
  abline(h = max(d$count))
  
  tbl = rbind(tbl, data.frame(
    File = file,
    Runtime = paste0(max(d$time) %/% 60, "m ", round(max(d$time)) %% 60, "s"),
    Count = max(d$count),
    PPM = round(max(d$count) / max(d$time) * 60, 1),
    Jaccard05 = round(mean(d$jac_sim == 0.5)*100, 3)
  ))
}

print(tbl)
