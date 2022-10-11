# combine from matlab ####
"Y:/Sheldon/All_WDIL/WDIL002_SyngapKO_high_stim_3steps/TC Syngap1_wn_WDIL002/Step 2/Het/1571/20180813/2018813135033.mat"
dir<-setwd('/Users/smichael/Desktop/licks_test')
#dir<-setwd('/Volumes/MillerRumbaughLab/Vaissiere/Sheldon')
files<-list.files(dir, pattern = ".mat", recursive = TRUE, full.names = TRUE)
dirs<-dirname(files)



c<-Sys.time()
out<-NULL
i<-NULL

for (i in dirs){
  
  mat<-list.files(i, pattern = ".mat", recursive = FALSE, full.names = TRUE)
  # careful there are some error in the files sometime duplicate or partial this code address that
  if (length(mat) >= 1){
    a<-file.info(mat)
    mat<-readMat(rownames(a[which(a$size == max(a$size)),]))
  }
  
  mat<-rbindlist(mat)
  mat<-lapply(mat, data.frame)
  mat<-Map(cbind, mat, X7=names(mat), X8=length(mat))
  mat<-rbindlist(mat)
  
  mat<-mat[,c(1,2,3,4,7,8)] #mat$X2==1
  colnames(mat)<-c("state.mat1","lick.trigg","time.s","state.mat2","Trial.","trial.total.per.session") # lick = 1
  mat$Trial.<-gsub('V',"",mat$Trial.)
  mat$Trial.<-as.numeric(mat$Trial.)
  
  trial<-list.files(i, pattern = ".xlsx", recursive = FALSE, full.names = TRUE)
  exclude<-list.files(i, pattern = "~", recursive = FALSE, full.names = TRUE)
  trial<-trial[!trial %in% exclude]
  # careful there are some error in the files sometime duplicate or partial this code address that
  if (length(trial) >= 1){
    a<-file.info(trial)
    trial<-data.table(read.xlsx(rownames(a[which(a$size == max(a$size)),]), sheetIndex = 1))
  }
  trial<-trial[,1:16]
  mat<-merge(trial,mat, by="Trial.")
  
  
  
  mat$id<-basename(dirname(i))
  mat$session<-basename(i)
  
  out<-rbind(out, mat)
  
  # display progress
  print(paste(which(dirs == i) , "/", length(dirs), " - file:", i))
} 

write.csv(out,"MASTER.csv", row.names = FALSE) #this file cannot be read in xls


out<-data.table(read.csv("MASTER.csv"))

#to obtain response time 
resp.start<-out[which(out$state.mat1 == 6 & out$state.mat2 == 7), c("id","session","Trial.","time.s")]
resp.end<-out[which(out$state.mat1 == 8 & out$state.mat2 == 9 & out$lick.trigg ==1), c("id","session","Trial.","time.s")]
resp<-merge(resp.start, resp.end, by = c("id","session","Trial."))
resp$resp.time.s<-resp$time.s.y-resp$time.s.x
resp<-resp[,c(1,2,3,6)]

# once response time obtained table can be simplified
data<-out[out$lick.trigg == 1,]
data<-merge(resp, data, by = c("id","session","Trial."), all = TRUE)
data[ , lick.event := cumsum(lick.trigg), by = c("id","session","Trial.","state.mat1")]

# lick interval
state8<-data[data$state.mat1 == 8,c("id","session","Trial.","time.s")]
state9<-data[data$state.mat1 == 9,c("id","session","Trial.","time.s","state.mat1","lick.event")]
temp.state<-merge(state8, state9, by = c("id","session","Trial."))

temp.state<-rename(temp.state, c(time.s.x="state8.time.s",time.s.y="state9.time.s"))

temp.state<-transform(temp.state,
                      delta.from.state8=state9.time.s-state8.time.s)


test<-temp.state
test[ , lag.time := c(NA, delta.from.state8[-.N]) , by = c("id","session","Trial.")]
test[ , inter.lick.interval.per.trial := delta.from.state8 - lag.time]
test$flag.first.lick.delay.per.trial[is.na(test$lag.time)]<-1

test<-merge(test, data, by = c("id","session", "Trial.","state.mat1","lick.event"), all = TRUE)


write.csv(test,"outputtomfromMASTER.csv", row.names = FALSE)
