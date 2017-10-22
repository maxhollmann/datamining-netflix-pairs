library(plotrix)

d = read.csv("out/candidate_dist.csv", header = T)
d$rows = d$sig_len / d$bands

cat("Run IDs:\n")
for (run_id in levels(d$run_id)) {
  r = d[d$run_id == run_id, ][1, ]
  cat(paste0(as.character(run_id), 
             "   sig_len: ", r$sig_len, 
             "   bands: ", r$bands,
             "   rows: ", r$rows))
}

run_id = d$run_id[nrow(d)]
cat("\n\nUsing", as.character(run_id))


d = d[d$run_id == run_id, ]


d = d[!duplicated(d[, c("u1", "u2")]), ]

print(nrow(d))


fit = lm(jac_sim ~ sig_sim + I(sig_sim^2), d)
#print(summary(fit))

pred_sig = seq(0, 1, .001)
pred_jac = predict(fit, newdata = data.frame(sig_sim = pred_sig))


par(mfrow = c(1, 2))

plot(jac_sim ~ sig_sim, d, type = 'p')
abline(0, 1, col = "green", lwd = 2)
abline(h = .5)
lines(pred_sig, pred_jac, col = "red", lwd = 2)


print(paste("Found", sum(d$jac_sim >= .5), "/", nrow(d), "with true similarity >= .5"))

weighted.hist(d$jac_sim, d$weight)
