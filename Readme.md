# gitlab-query-testing

## Requirements

- GitLab Access Token
- Required Python libraries (gitlab, json, time, readline, sys, boto3, argpasre)

# Usage 

The GitLab query search has been made to help find SQL statments which appear inside of GitLab repositories, rather than manually searching for matches. As a general overview both the `LocalFindQuery.py` and `findQuery.py` scripts take in an argument of a string or list of words. These words or strings are then sorted and the longest 5 are searched. If a file conatins these 5 key words then the file along with a link to the repository they are found in, will be returned. The aim of this script is to help locate SQL queries and strings quickly. The scripts will only search the **Master / Main** branch.  

As a general rule of thumb longer SQL queries may work however if they do not return anything it is best practise to add 5 variables with a single space between and have no special characters inside (!, & , *) etc. If no result is returned at this stage then there is no match within GitLab.

For example 

```
This and this are valid
```

```
This & this aren't valid
```

The reason example 2 does not work is the special symbol

This Job uses the GitLab API in order to search through all repositories, as it does not change any code it can be run by anyone and no specific gitlab permissions are needed to use it. 

## Running Locally

The script `LocalFindQuery.py` is run locally. To use this script you will need to set a GitLab Access token as an Environmental variable. This can be done by running the following on windows:

```
nano ~/.bashrc

EXPORT GITLAB_ACCESS_TOKEN=xyz # Add this line to the file

```

For Mac:

```
nano ~/.zshrc

EXPORT GITLAB_ACCESS_TOKEN=xyz # Add this line to the file
```

When run, it takes a single argument through the command line, the String / Query entered will be split up and the longest 5 words will be sorted and searched. This allows for high accurancy for finding the file with the matched words while limiting results to only a few files. Common words such as "as, and , where , select" etc are removed from the input to further the accuracy and make the search results more specific. Any search results will be printed inside of Jenkins including the file and repository link.

## Running through Jenkins

The Script `findQuery.py` can be found **redacted** and is run through Jenkins. It takes a single argument of a String or Query and when `build` is pressed the search is started. Any search results will be printed inside of Jenkins including the file and repository link. 

# Examples

To search for the query :

```
select orderId,customerName,shippingAddress,productCode,totalAmount,orderDate,region,isPriority,pk_order,isShipped,warehouseId,deliveryStatus,user_def_1,(orderId) as search_key from (select o.pk_order as pk_order,o.order_id as orderId,o.customer_name as customerName,o.total_amount as totalAmount,o.order_date as orderDate,o.region as region,(select w.name from wh_warehouse w where w.pk_warehouse=o.pk_warehouse) as warehouseId,(select w.pk_warehouse from wh_warehouse w where w.pk_warehouse=o.pk_warehouse) as warehouseKey,(select LISTAGG(item.product_code, ' ') within group (order by item.product_code) from order_items item where item.pk_order=o.pk_order) as productCode,(select LISTAGG(tag.tag_name, ' ') within group (order by tag.tag_name) from order_tags tag where tag.pk_order=o.pk_order) as deliveryStatus,(select 1 from shipments s where s.pk_order=o.pk_order and s.is_priority=1) as isPriority,(select 1 from shipments s where s.pk_order=o.pk_order and s.is_shipped=1) as isShipped,(select c.vip_status from customers c where c.pk_customer=o.pk_customer) as user_def_1 from sales_orders o where o.active=1 and o.total_amount > 100)

```

You would include lines / words which contain no special characters. For example you could enter :
```
select orderId,customerName,shippingAddress,productCode,totalAmount,orderDate
```

This woud sucessfully search and find the Query as there is no special characters or spaces in between words.

The script breaks down the entered input and gets the 5 longest words, in this case it is
**shippingAddress, deliveryStatus, customerName, warehouseId, totalAmount.** 